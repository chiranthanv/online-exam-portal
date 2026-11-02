"""Unique synthetic records for recovery E2E; never modify an existing account."""

import json
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from portal.models import (
    AttemptAnswer,
    Batch,
    Exam,
    ExamAttempt,
    ExamBatch,
    ExamQuestion,
    Question,
    StudentBatch,
    User,
)

if not settings.DEBUG or User.objects.exclude(email__endswith="@example.test").exists():
    raise RuntimeError("Recovery E2E requires a disposable synthetic development database")

suffix = uuid.uuid4().hex[:12]
student = User.objects.create_user(
    username="recovery-" + suffix,
    email="recovery-" + suffix + "@example.test",
    name="Recovery fixture",
    usn="R" + suffix,
    role="STUDENT",
    password="Recovery-Fixture-Password-123!",
)
admin = User.objects.get(email="demo-admin@example.test")
question = Question.objects.filter(created_by=admin).order_by("id").first()
if question is None:
    raise RuntimeError("Run seed_demo before browser tests")
batch = Batch.objects.create(name="Recovery " + suffix, year=2026)
StudentBatch.objects.create(student=student, batch=batch)
now = timezone.now()
completed = os.getenv("RECOVERY_FIXTURE_COMPLETED") == "1"
exam = Exam.objects.create(
    title="Recovery " + suffix,
    created_by=admin,
    duration_minutes=30,
    start_time=now - timedelta(hours=2) if completed else now - timedelta(minutes=1),
    end_time=now - timedelta(hours=1) if completed else now + timedelta(hours=1),
    result_visible_from=now - timedelta(minutes=1) if completed else now + timedelta(hours=2),
    total_marks=question.default_marks,
)
ExamQuestion.objects.create(exam=exam, question=question, sequence=1)
ExamBatch.objects.create(exam=exam, batch=batch)
if completed:
    attempt = ExamAttempt.objects.create(
        exam=exam,
        student=student,
        status=ExamAttempt.SUBMITTED,
        started_at=now - timedelta(hours=2),
        deadline_at=now - timedelta(hours=1),
        submitted_at=now - timedelta(hours=1),
        evaluated_at=now - timedelta(hours=1),
        score=question.default_marks,
    )
    AttemptAnswer.objects.create(
        attempt=attempt,
        question=question,
        selected_option_id=question.options.get(is_correct=True).id,
    )
print(
    "RECOVERY_FIXTURE="
    + json.dumps(
        {
            "email": student.email,
            "exam_id": str(exam.id),
            "title": exam.title,
            "score": str(question.default_marks),
        }
    )
)
