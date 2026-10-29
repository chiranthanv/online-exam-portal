"""Seed synthetic data and short-lived credentials into a NEW disposable database."""

import json
import os
import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from portal.models import (
    AttemptAnswer,
    Batch,
    Exam,
    ExamAttempt,
    ExamBatch,
    ExamQuestion,
    Option,
    Question,
    StudentBatch,
    User,
)


class Command(BaseCommand):
    help = "Seed exactly 200 load students, 5 browser students, 50 MCQs and historical answers."

    def add_arguments(self, parser):
        parser.add_argument("--manifest", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        if (
            os.getenv("PERF_DISPOSABLE") != "1"
            or connection.vendor != "postgresql"
            or not settings.DATABASES["default"]["NAME"].startswith("oep_perf_")
            or User.objects.exists()
        ):
            raise CommandError("Requires a NEW empty disposable PostgreSQL oep_perf_* database.")
        admin = User.objects.create(username="perf-admin", email="perf-admin@example.test", role="ADMIN")
        password = "Disposable-Perf-Only-827!"
        hashed = make_password(password)
        students = [
            User(
                username=f"perf-{i}",
                email=f"perf-{i}@example.test",
                name=f"Synthetic student {i}",
                usn=f"PERF{i:04}",
                password=hashed,
            )
            for i in range(205)
        ]
        User.objects.bulk_create(students)
        batch = Batch.objects.create(name="PERF-200", year=2026)
        StudentBatch.objects.bulk_create([StudentBatch(student=s, batch=batch) for s in students])
        questions = [
            Question(
                text=f"[PERF {i + 1:02}] Which operation preserves a database transaction's atomicity?",
                subject="DBMS",
                topic="Transactions",
                difficulty="MEDIUM",
                default_marks=2,
                negative_marks="0.5",
                created_by=admin,
            )
            for i in range(50)
        ]
        Question.objects.bulk_create(questions)
        Option.objects.bulk_create(
            [
                Option(question=q, text=f"Option {j}: " + "synthetic exam content " * 5, is_correct=j == 0)
                for q in questions
                for j in range(4)
            ]
        )
        choices = {q.id: q.options.first().id for q in questions}
        now = timezone.now()
        exams = []
        for title in ("[PERF] Current class", "[PERF] Historical class"):
            exam = Exam.objects.create(
                title=title,
                created_by=admin,
                duration_minutes=30,
                start_time=now - timedelta(minutes=1),
                end_time=now + timedelta(hours=2),
                result_visible_from=now + timedelta(hours=3),
                total_marks=100,
            )
            ExamBatch.objects.create(exam=exam, batch=batch)
            ExamQuestion.objects.bulk_create(
                [ExamQuestion(exam=exam, question=q, sequence=i) for i, q in enumerate(questions, 1)]
            )
            exams.append(exam)
        history = [
            ExamAttempt(
                exam=exams[1],
                student=s,
                status=ExamAttempt.SUBMITTED,
                deadline_at=now,
                submitted_at=now,
            )
            for s in students[:200]
        ]
        ExamAttempt.objects.bulk_create(history)
        AttemptAnswer.objects.bulk_create(
            [
                AttemptAnswer(attempt=a, question=q, selected_option_id=choices[q.id])
                for a in history
                for q in questions
            ],
            batch_size=1000,
        )
        identities = []
        for s in students:
            token = AccessToken.for_user(s)
            token["av"] = s.auth_version
            token.set_exp(lifetime=timedelta(minutes=30))
            identities.append({"student_id": str(s.id), "token": str(token), "session": str(uuid.uuid4())})
        manifest = {
            "exam_id": str(exams[0].id),
            "question_count": 50,
            "students": identities[:200],
            "browser_accounts": [{"email": s.email, "password": password} for s in students[200:]],
            "created_at": now.isoformat(),
        }
        path = Path(options["manifest"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest))
        path.chmod(0o600)
        self.stdout.write("Seeded 200 load + 5 browser users, 50 MCQs, 10,000 historical answers.")
