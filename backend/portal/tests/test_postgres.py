"""Real row-lock regressions; run in PostgreSQL CI, explicitly skipped on SQLite."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection, connections
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import AttemptAnswer, AuditLog, Exam, ExamAttempt, ExamQuestion, Option, Question, User
from portal.services import select_questions


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row locks; executed by CI")
class PostgreSQLConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.password = "Concurrent-Test-Passphrase-726!"
        self.admin = User.objects.create_user(
            username="admin", email="admin@example.test", role="ADMIN", password=self.password
        )

    def client_with_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        csrf = client.get("/api/v1/auth/csrf").json()["csrf_token"]
        client.credentials(HTTP_X_CSRFTOKEN=csrf)
        return client

    def test_parallel_login_failures_do_not_lose_increments(self):
        barrier = Barrier(6)

        def fail_login(_):
            close_old_connections()
            try:
                client = self.client_with_csrf()
                barrier.wait(timeout=10)
                return client.post(
                    "/api/v1/auth/login", {"email": self.admin.email, "password": "wrong"}, format="json"
                ).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=6) as executor:
            statuses = list(executor.map(fail_login, range(6)))
        self.assertEqual(sorted(statuses), [401] * 5 + [423])
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.failed_logins, 5)

    def test_concurrent_refresh_accepts_token_once(self):
        client = self.client_with_csrf()
        response = client.post(
            "/api/v1/auth/login", {"email": self.admin.email, "password": self.password}, format="json"
        )
        raw = response.cookies["oep_refresh"].value
        barrier = Barrier(2)

        def refresh(_):
            close_old_connections()
            try:
                client = self.client_with_csrf()
                client.cookies["oep_refresh"] = raw
                barrier.wait(timeout=10)
                return client.post("/api/v1/auth/refresh", {}, format="json").status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(refresh, range(2)))
        self.assertEqual(sorted(statuses), [200, 401])

    def test_concurrent_question_replacement_keeps_consistent_total(self):
        now = timezone.now()
        exam = Exam.objects.create(
            title="Concurrent",
            created_by=self.admin,
            duration_minutes=30,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            result_visible_from=now + timedelta(hours=3),
        )
        questions = [
            Question.objects.create(
                text=str(i),
                subject="SE",
                topic="Testing",
                difficulty="EASY",
                default_marks=i + 1,
                created_by=self.admin,
            )
            for i in range(4)
        ]
        choices = [[q.id for q in questions[:2]], [q.id for q in questions[2:]]]
        barrier = Barrier(2)

        def replace(ids):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                select_questions(exam.id, {"mode": "manual", "question_ids": ids}, self.admin)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(replace, choices))
        exam.refresh_from_db()
        selected = list(exam.questions.all())
        self.assertIn({q.id for q in selected}, [{pk for pk in ids} for ids in choices])
        self.assertEqual(exam.total_marks, sum(q.default_marks for q in selected))

    def test_attempt_read_does_not_lock_shared_exam_row(self):
        """A lock on the shared exam must not serialize every student's attempt read."""
        import uuid

        from django.db import transaction

        from portal.models import ExamAttempt

        now = timezone.now()
        exam = Exam.objects.create(
            title="Independent attempt locks",
            created_by=self.admin,
            duration_minutes=30,
            start_time=now - timedelta(minutes=1),
            end_time=now + timedelta(hours=1),
            result_visible_from=now + timedelta(hours=2),
        )
        student = User.objects.create_user(username="lock-student", email="lock@example.test")
        attempt = ExamAttempt.objects.create(
            exam=exam, student=student, session_key=uuid.uuid4(), deadline_at=now + timedelta(minutes=30)
        )

        def read_attempt():
            close_old_connections()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET lock_timeout = '500ms'")
                client = APIClient()
                client.force_authenticate(student)
                return client.get(
                    f"/api/v1/attempts/{attempt.id}", HTTP_X_EXAM_SESSION=str(attempt.session_key)
                ).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=1) as executor:
            with transaction.atomic():
                Exam.objects.select_for_update().get(pk=exam.pk)
                self.assertEqual(executor.submit(read_attempt).result(timeout=10), 200)

    def test_save_submit_race_cannot_modify_closed_answers(self):
        student = User.objects.create_user(username="racer", email="race@example.test")
        now = timezone.now()
        exam = Exam.objects.create(
            title="Save/submit race",
            created_by=self.admin,
            duration_minutes=30,
            start_time=now - timedelta(minutes=1),
            end_time=now + timedelta(hours=1),
            result_visible_from=now + timedelta(hours=2),
            total_marks=2,
        )
        question = Question.objects.create(
            text="Race",
            subject="SE",
            topic="Transactions",
            difficulty="EASY",
            default_marks=2,
            created_by=self.admin,
        )
        option = Option.objects.create(question=question, text="A", is_correct=True)
        ExamQuestion.objects.create(exam=exam, question=question, sequence=1)
        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=student,
            deadline_at=now + timedelta(minutes=30),
        )
        barrier = Barrier(2)

        def request(submit):
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(user=student)
                client.credentials(HTTP_X_EXAM_SESSION=str(attempt.session_key))
                barrier.wait(timeout=10)
                if submit:
                    return client.post(f"/api/v1/attempts/{attempt.id}/submit", {}, format="json").status_code
                return client.patch(
                    f"/api/v1/attempts/{attempt.id}/answers",
                    {
                        "question_id": str(question.id),
                        "option_id": str(option.id),
                    },
                    format="json",
                ).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            saved, submitted = list(executor.map(request, [False, True]))
        self.assertIn(saved, [200, 409])
        self.assertEqual(submitted, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.SUBMITTED)
        snapshot = list(AttemptAnswer.objects.filter(attempt=attempt).values())
        client = APIClient()
        client.force_authenticate(user=student)
        client.credentials(HTTP_X_EXAM_SESSION=str(attempt.session_key))
        rejected = client.patch(
            f"/api/v1/attempts/{attempt.id}/answers",
            {
                "question_id": str(question.id),
                "option_id": None,
            },
            format="json",
        )
        self.assertEqual(rejected.status_code, 409)
        self.assertEqual(list(AttemptAnswer.objects.filter(attempt=attempt).values()), snapshot)
        self.assertEqual(
            AuditLog.objects.filter(action="EXAM_ATTEMPT_SUBMITTED", target=str(attempt.id)).count(), 1
        )
