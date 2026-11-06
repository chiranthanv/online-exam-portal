"""Part 3 follow-up: two real database sessions starting the same exam attempt."""

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.db import close_old_connections, connection, connections
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import (
    AuditLog,
    Batch,
    Exam,
    ExamAttempt,
    ExamBatch,
    ExamQuestion,
    Question,
    StudentBatch,
    User,
)
from portal.views import _lock_exam_for_attempt_start


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL concurrent transactions; executed by CI")
class ConcurrentAttemptStartTests(TransactionTestCase):
    def test_simultaneous_sessions_create_one_attempt_and_only_winner_can_resume(self):
        admin = User.objects.create_user(username="race-admin", email="race-admin@example.test", role="ADMIN")
        student = User.objects.create_user(username="race-student", email="race-student@example.test")
        batch = Batch.objects.create(name="Concurrent attempt test", year=2026)
        StudentBatch.objects.create(student=student, batch=batch)
        now = timezone.now()
        exam = Exam.objects.create(
            title="Concurrent attempt start",
            created_by=admin,
            duration_minutes=30,
            start_time=now - timedelta(minutes=1),
            end_time=now + timedelta(hours=1),
            result_visible_from=now + timedelta(hours=2),
            total_marks="1.00",
        )
        question = Question.objects.create(
            text="Concurrent-start fixture", subject="SE", topic="Concurrency", created_by=admin
        )
        ExamQuestion.objects.create(exam=exam, question=question, sequence=1)
        ExamBatch.objects.create(exam=exam, batch=batch)
        session_ids = [uuid.uuid4(), uuid.uuid4()]
        both_inside_start = Barrier(2)

        def lock_then_meet(exam_id):
            locked_exam = _lock_exam_for_attempt_start(exam_id)
            # Both real transactions reach the start path before either is
            # allowed to create an attempt. This avoids a sequential false pass.
            both_inside_start.wait(timeout=10)
            return locked_exam

        def start(session_id):
            close_old_connections()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET lock_timeout = '5s'")
                client = APIClient()
                client.force_authenticate(student)
                response = client.post(
                    f"/api/v1/exams/{exam.id}/attempt",
                    {"session_id": str(session_id)},
                    format="json",
                    HTTP_X_EXAM_SESSION=str(session_id),
                )
                return session_id, response.status_code
            finally:
                connections.close_all()

        with patch("portal.views._lock_exam_for_attempt_start", side_effect=lock_then_meet):
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(start, session_id) for session_id in session_ids]
                outcomes = [future.result(timeout=20) for future in futures]

        self.assertEqual(sorted(status for _, status in outcomes), [201, 409], outcomes)
        self.assertEqual(ExamAttempt.objects.filter(exam=exam, student=student).count(), 1)
        attempt = ExamAttempt.objects.get(exam=exam, student=student)
        winner = next(session_id for session_id, status in outcomes if status == 201)
        self.assertEqual(attempt.session_key, winner)
        self.assertEqual(
            AuditLog.objects.filter(action="EXAM_ATTEMPT_STARTED", target=str(attempt.id)).count(), 1
        )
        for session_id, original_status in outcomes:
            client = APIClient()
            client.force_authenticate(student)
            response = client.get(f"/api/v1/attempts/{attempt.id}", HTTP_X_EXAM_SESSION=str(session_id))
            self.assertEqual(response.status_code, 200 if original_status == 201 else 409)
