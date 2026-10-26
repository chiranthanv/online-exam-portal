"""Real row-lock regressions; run in PostgreSQL CI, explicitly skipped on SQLite."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import Exam, Question, User
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
                close_old_connections()

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
                close_old_connections()

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
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(replace, choices))
        exam.refresh_from_db()
        selected = list(exam.questions.all())
        self.assertIn({q.id for q in selected}, [{pk for pk in ids} for ids in choices])
        self.assertEqual(exam.total_marks, sum(q.default_marks for q in selected))
