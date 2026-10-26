"""Create repeatable synthetic demo data; never run against a production database."""

import os
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from portal.models import Batch, Exam, ExamBatch, ExamQuestion, Option, Question, StudentBatch, User


class Command(BaseCommand):
    help = "Seed local demo accounts, 3 batches, 50 questions and an available exam (DEBUG only)."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo is disabled when DEBUG=0.")
        password = os.getenv("DEMO_PASSWORD", "Local-Demo-Only-827!")
        users = []
        for username, role, usn in [
            ("demo-admin", "ADMIN", None),
            ("demo-student", "STUDENT", "DEMO001"),
            ("demo-other", "STUDENT", "DEMO002"),
        ]:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": username + "@example.test",
                    "name": username.replace("-", " ").title(),
                    "role": role,
                    "usn": usn,
                },
            )
            if not created and (user.email != username + "@example.test" or user.role != role):
                raise CommandError(
                    "Demo username conflicts with existing data; use a fresh development database."
                )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            users.append(user)
        admin, student, other = users
        batches = [
            Batch.objects.get_or_create(name=f"DEMO-CSE-{name}", defaults={"year": 2026})[0]
            for name in ("A", "B", "C")
        ]
        StudentBatch.objects.get_or_create(student=student, batch=batches[0])
        StudentBatch.objects.get_or_create(student=other, batch=batches[1])
        questions = []
        for i in range(50):
            question, created = Question.objects.get_or_create(
                text=f"[DEMO {i + 1:02}] Which activity verifies expected software behavior?",
                created_by=admin,
                defaults={
                    "subject": "Software Engineering",
                    "topic": "Testing",
                    "difficulty": ["EASY", "MEDIUM", "HARD"][i % 3],
                    "default_marks": Decimal("2.00"),
                    "negative_marks": Decimal("0.50"),
                },
            )
            if created:
                Option.objects.bulk_create(
                    [
                        Option(question=question, text="Testing", is_correct=True),
                        Option(question=question, text="Ignoring defects"),
                        Option(question=question, text="Removing all assertions"),
                    ]
                )
            questions.append(question)
        now = timezone.now()
        # This explicit demo command renews only its named synthetic exam window.
        exam, _ = Exam.objects.update_or_create(
            title="[DEMO] Available practice exam",
            created_by=admin,
            defaults={
                "start_time": now - timedelta(minutes=1),
                "end_time": now + timedelta(hours=2),
                "result_visible_from": now + timedelta(hours=3),
                "duration_minutes": 30,
                "total_marks": Decimal("10.00"),
            },
        )
        ExamQuestion.objects.filter(exam=exam).delete()
        ExamQuestion.objects.bulk_create(
            [ExamQuestion(exam=exam, question=q, sequence=i) for i, q in enumerate(questions[:5], 1)]
        )
        ExamBatch.objects.get_or_create(exam=exam, batch=batches[0])
        self.stdout.write(
            self.style.SUCCESS("Demo ready: 3 users, 3 batches, 50 questions, 1 available exam.")
        )
        self.stdout.write(
            "Accounts: demo-admin@example.test, demo-student@example.test, demo-other@example.test"
        )
        self.stdout.write(
            "New accounts use DEMO_PASSWORD, or the development-only password documented in README. Existing passwords are preserved."
        )
