"""Capture real planner choices; do not force index scans on small fixtures."""

import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from portal.models import AttemptAnswer, ExamAttempt, ExamQuestion, Option


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        if (
            connection.vendor != "postgresql"
            or os.getenv("PERF_DISPOSABLE") != "1"
            or not settings.DATABASES["default"]["NAME"].startswith("oep_perf_")
        ):
            raise CommandError("EXPLAIN evidence requires PostgreSQL.")
        attempt = ExamAttempt.objects.filter(answers__isnull=False).first()
        if not attempt:
            raise CommandError("Seed synthetic attempts first.")
        answer = attempt.answers.first()
        queries = {
            "attempt_exam_student": ExamAttempt.objects.filter(
                exam_id=attempt.exam_id, student_id=attempt.student_id
            ),
            "response_attempt": AttemptAnswer.objects.filter(attempt_id=attempt.id),
            "response_attempt_question": AttemptAnswer.objects.filter(
                attempt_id=attempt.id, question_id=answer.question_id
            ),
            "ordered_exam_questions": ExamQuestion.objects.filter(exam_id=attempt.exam_id),
            "question_options": Option.objects.filter(question_id=answer.question_id),
        }
        with connection.cursor() as cursor:
            # All data is synthetic; ANALYZE refreshes statistics in this disposable DB only.
            cursor.execute("ANALYZE")
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.execute(
                "SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname"
            )
            indexes = cursor.fetchall()
        result = {"postgres_version": version, "indexes": indexes, "plans": {}}
        for name, query in queries.items():
            result["plans"][name] = json.loads(query.explain(format="JSON", analyze=True, buffers=True))
        Path(options["output"]).write_text(json.dumps(result, indent=2))
        self.stdout.write("Captured ANALYZE/BUFFERS plans and index definitions.")
