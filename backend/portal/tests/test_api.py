import hashlib
import io
import re
import smtplib
import uuid
from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from openpyxl import Workbook
from rest_framework.test import APIClient

from portal.models import (
    AttemptAnswer,
    AuditLog,
    Batch,
    Exam,
    ExamAttempt,
    ExamBatch,
    ExamQuestion,
    Option,
    PasswordResetGrant,
    Question,
    StudentBatch,
    User,
)

PASSWORD = "Test-Only-Passphrase-491!"


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", email="admin@example.test", name="Faculty", role="ADMIN", password=PASSWORD
        )
        cls.student = User.objects.create_user(
            username="student", email="student@example.test", name="Student", usn="S001", password=PASSWORD
        )
        cls.other = User.objects.create_user(
            username="other", email="other@example.test", name="Other", usn="S002", password=PASSWORD
        )
        cls.batch = Batch.objects.create(name="CSE-A", year=2026)
        cls.batch2 = Batch.objects.create(name="CSE-B", year=2026)
        StudentBatch.objects.create(student=cls.student, batch=cls.batch)
        cls.questions = []
        for i, difficulty in enumerate(["EASY", "EASY", "MEDIUM", "HARD"]):
            q = Question.objects.create(
                text=f"Question {i}",
                subject="SE",
                topic="Testing",
                difficulty=difficulty,
                default_marks="2.00",
                negative_marks="0.50",
                created_by=cls.admin,
            )
            Option.objects.create(question=q, text="Correct", is_correct=True)
            Option.objects.create(question=q, text="Wrong")
            cls.questions.append(q)
        now = timezone.now()
        cls.exam = Exam.objects.create(
            title="Sprint 1",
            duration_minutes=30,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            result_visible_from=now + timedelta(hours=3),
            created_by=cls.admin,
        )

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.csrf = self.client.get("/api/v1/auth/csrf").json()["csrf_token"]
        self.client.credentials(HTTP_X_CSRFTOKEN=self.csrf)

    def login(self, user=None, password=PASSWORD):
        user = user or self.admin
        result = self.client.post(
            "/api/v1/auth/login", {"email": user.email, "password": password}, format="json"
        )
        if result.status_code == 200:
            self.client.credentials(
                HTTP_X_CSRFTOKEN=self.csrf, HTTP_AUTHORIZATION="Bearer " + result.json()["access_token"]
            )
        return result

    def post(self, url, payload):
        return self.client.post("/api/v1/" + url, payload, format="json")

    def question_payload(self):
        return dict(
            text="What is testing?",
            subject="SE",
            topic="Testing",
            difficulty="EASY",
            default_marks="3.00",
            negative_marks="0.25",
            options=[{"text": "Verification", "is_correct": True}, {"text": "Nothing", "is_correct": False}],
        )

    def select(self, **data):
        return self.post(f"exams/{self.exam.id}/questions", data)

    def reset_token(self):
        result = self.post(f"auth/students/{self.student.id}/reset-password", {})
        self.assertEqual(result.status_code, 200, result.content)
        return re.search(r"token=([A-Za-z0-9_-]+)", mail.outbox[-1].body).group(1)

    def test_login_hash_role_and_cookie(self):
        result = self.login()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["role"], "ADMIN")
        self.assertTrue(result.cookies["oep_refresh"]["httponly"])
        self.assertEqual(result.cookies["oep_refresh"]["samesite"], "Lax")
        self.assertNotIn("refresh_token", result.json())
        self.assertTrue(self.admin.password.startswith("argon2$"))
        self.assertNotEqual(self.student.password, self.other.password)
        self.assertEqual(self.client.get("/api/v1/auth/me").json()["email"], self.admin.email)

    def test_login_and_refresh_require_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        for route in ("login", "refresh", "reset-password/confirm"):
            self.assertEqual(client.post("/api/v1/auth/" + route, {}, format="json").status_code, 403)

    def test_unknown_user_and_bad_password_are_identical(self):
        bad = self.login(password="wrong").json()
        unknown = self.client.post(
            "/api/v1/auth/login", {"email": "absent@example.test", "password": "wrong"}, format="json"
        )
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(bad, unknown.json())

    def test_five_failures_lock_sixth_even_correct(self):
        for _ in range(5):
            self.assertEqual(self.login(password="wrong").status_code, 401)
        self.assertEqual(self.login().status_code, 423)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.failed_logins, 5)
        self.assertTrue(
            timezone.now() + timedelta(minutes=14)
            < self.admin.locked_until
            <= timezone.now() + timedelta(minutes=15)
        )

    def test_expired_lock_allows_login_and_resets_counter(self):
        User.objects.filter(pk=self.admin.pk).update(
            failed_logins=5, locked_until=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(self.login().status_code, 200)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.failed_logins, 0)
        self.assertIsNone(self.admin.locked_until)

    def test_success_resets_prior_failure(self):
        self.login(password="wrong")
        self.login()
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.failed_logins, 0)

    def test_refresh_rotates_and_rejects_replay(self):
        self.login()
        old = self.client.cookies["oep_refresh"].value
        result = self.post("auth/refresh", {})
        self.assertEqual(result.status_code, 200)
        self.assertNotEqual(old, result.cookies["oep_refresh"].value)
        self.client.cookies["oep_refresh"] = old
        self.assertEqual(self.post("auth/refresh", {}).status_code, 401)

    def test_logout_revokes_access_and_refresh(self):
        self.login()
        refresh = self.client.cookies["oep_refresh"].value
        self.assertEqual(self.post("auth/logout", {}).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 401)
        self.client.cookies["oep_refresh"] = refresh
        self.assertEqual(self.post("auth/refresh", {}).status_code, 401)

    def test_inactive_user_cannot_login(self):
        User.objects.filter(pk=self.admin.pk).update(is_active=False)
        self.assertEqual(self.login().status_code, 401)

    def test_reset_single_use_hashed_and_one_hour(self):
        self.login()
        token = self.reset_token()
        grant = PasswordResetGrant.objects.get()
        self.assertEqual(grant.token_hash, hashlib.sha256(token.encode()).hexdigest())
        self.assertTrue(
            timezone.now() + timedelta(minutes=59) < grant.expires_at <= timezone.now() + timedelta(hours=1)
        )
        payload = {"token": token, "password": "New-Long-Passphrase-657!"}
        self.assertEqual(self.post("auth/reset-password/confirm", payload).status_code, 200)
        self.assertEqual(self.post("auth/reset-password/confirm", payload).status_code, 400)
        self.assertEqual(self.login(self.student, payload["password"]).status_code, 200)

    def test_reset_revokes_student_session_immediately(self):
        access = self.login(self.student).json()["access_token"]
        self.login()
        self.reset_token()
        self.client.credentials(HTTP_X_CSRFTOKEN=self.csrf, HTTP_AUTHORIZATION="Bearer " + access)
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 401)
        self.assertEqual(self.login(self.student).status_code, 401)

    def test_new_reset_invalidates_previous_link(self):
        self.login()
        old = self.reset_token()
        self.reset_token()
        self.assertEqual(
            self.post("auth/reset-password/confirm", {"token": old, "password": PASSWORD}).status_code, 400
        )

    def test_expired_reset_and_unknown_reset_rejected(self):
        self.login()
        token = self.reset_token()
        PasswordResetGrant.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        for value in (token, "invalid-token-of-adequate-length"):
            self.assertEqual(
                self.post("auth/reset-password/confirm", {"token": value, "password": PASSWORD}).status_code,
                400,
            )

    def test_weak_password_does_not_consume_link(self):
        self.login()
        token = self.reset_token()
        self.assertEqual(
            self.post("auth/reset-password/confirm", {"token": token, "password": "password123"}).status_code,
            400,
        )
        self.assertIsNone(PasswordResetGrant.objects.get().consumed_at)

    @patch("portal.auth_views.send_mail", side_effect=smtplib.SMTPException("offline"))
    def test_email_failure_rolls_back_reset(self, mocked):
        self.login()
        self.assertEqual(self.post(f"auth/students/{self.student.id}/reset-password", {}).status_code, 503)
        self.student.refresh_from_db()
        self.assertFalse(self.student.must_reset_password)
        self.assertEqual(self.student.auth_version, 0)
        self.assertFalse(PasswordResetGrant.objects.exists())

    def test_role_matrix_for_all_admin_routes(self):
        routes = [
            ("get", "students"),
            ("post", "students/bulk-import"),
            ("get", "batches"),
            ("post", "batches"),
            ("get", f"batches/{self.batch.id}/students"),
            ("post", f"batches/{self.batch.id}/students"),
            ("get", "questions"),
            ("post", "questions"),
            ("get", f"questions/{self.questions[0].id}"),
            ("put", f"questions/{self.questions[0].id}"),
            ("patch", f"questions/{self.questions[0].id}"),
            ("delete", f"questions/{self.questions[0].id}"),
            ("get", "exams"),
            ("post", "exams"),
            ("get", f"exams/{self.exam.id}"),
            ("put", f"exams/{self.exam.id}"),
            ("patch", f"exams/{self.exam.id}"),
            ("get", f"exams/{self.exam.id}/questions"),
            ("post", f"exams/{self.exam.id}/questions"),
            ("post", f"exams/{self.exam.id}/batches"),
            ("post", f"auth/students/{self.student.id}/reset-password"),
            ("get", "audit-logs"),
        ]
        for user, expected in ((None, 401), (self.student, 403)):
            if user:
                self.login(user)
            for method, route in routes:
                with self.subTest(role=user.role if user else "ANON", method=method, route=route):
                    response = getattr(self.client, method)("/api/v1/" + route)
                    self.assertEqual(response.status_code, expected, response.content)
                    self.assertNotIn("is_correct", response.content.decode())

    def upload_csv(self, contents):
        return self.client.post(
            "/api/v1/students/bulk-import",
            {"file": SimpleUploadedFile("roster.csv", contents.encode(), content_type="text/csv")},
            format="multipart",
        )

    def test_csv_partial_import_with_exact_row_errors(self):
        self.login()
        result = self.upload_csv(
            "name,email,usn,batch\nNew,new@example.test,s003,CSE-A|CSE-B\nBad,not-email,S004,CSE-A\nDuplicate,new@example.test,S005,CSE-A\nMissing,missing@example.test,S006,Unknown\n"
        )
        self.assertEqual(result.status_code, 207)
        self.assertEqual(result.json()["created"], 1)
        self.assertEqual([x["row"] for x in result.json()["errors"]], [3, 4, 5])
        student = User.objects.get(usn="S003")
        self.assertEqual(student.batches.count(), 2)
        self.assertFalse(student.has_usable_password())
        self.assertTrue(student.must_reset_password)
        self.assertFalse(User.objects.filter(email="missing@example.test").exists())

    def test_csv_all_valid_and_casefold_duplicates(self):
        self.login()
        self.assertEqual(
            self.upload_csv("name,email,usn,batch\nNew,new@example.test,S003,CSE-A").status_code, 201
        )
        result = self.upload_csv(
            "name,email,usn,batch\nDup,NEW@example.test,S004,CSE-A\nDup2,different@example.test,s003,CSE-A"
        )
        self.assertEqual(result.json()["created"], 0)
        self.assertEqual(len(result.json()["errors"]), 2)

    def test_csv_invalid_headers_empty_and_missing_file(self):
        self.login()
        for text in ("", "name,email,usn,batch\n", "email,name,usn,batch\na,b,c,d"):
            self.assertEqual(self.upload_csv(text).status_code, 400)
        self.assertEqual(
            self.client.post("/api/v1/students/bulk-import", {}, format="multipart").status_code, 400
        )

    def test_xlsx_import_and_formula_rejection(self):
        self.login()
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["name", "email", "usn", "batch"])
        sheet.append(["Excel", "excel@example.test", "S004", "CSE-B"])
        for formula, expected in ((False, 201), (True, 400)):
            if formula:
                sheet["A2"] = "=1+1"
            stream = io.BytesIO()
            workbook.save(stream)
            response = self.client.post(
                "/api/v1/students/bulk-import",
                {"file": SimpleUploadedFile("roster.xlsx", stream.getvalue())},
                format="multipart",
            )
            self.assertEqual(response.status_code, expected, response.content)

    def test_invalid_and_oversized_roster_files(self):
        self.login()
        for name, data in [
            ("roster.xlsx", b"not zip"),
            ("roster.exe", b"hello"),
            ("roster.csv", b"x" * (2 * 1024 * 1024 + 1)),
        ]:
            result = self.client.post(
                "/api/v1/students/bulk-import", {"file": SimpleUploadedFile(name, data)}, format="multipart"
            )
            self.assertEqual(result.status_code, 400)

    def test_batch_creation_and_idempotent_membership(self):
        self.login()
        self.assertEqual(self.post("batches", {"name": "NEW", "year": 2026}).status_code, 201)
        self.assertEqual(self.post("batches", {"name": "Bad", "year": 0}).status_code, 400)
        for expected in (1, 0):
            result = self.post(
                f"batches/{self.batch.id}/students", {"student_ids": [str(self.other.id), str(self.other.id)]}
            )
            self.assertEqual(result.json()["mapped"], expected)
        self.assertEqual(
            self.post(f"batches/{self.batch.id}/students", {"student_ids": [str(self.admin.id)]}).status_code,
            400,
        )

    def test_unknown_membership_id_rolls_back_whole_request(self):
        self.login()
        result = self.post(
            f"batches/{self.batch2.id}/students", {"student_ids": [str(self.other.id), str(uuid.uuid4())]}
        )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(self.batch2.students.count(), 0)

    def test_question_crud_filter_and_audit(self):
        self.login()
        result = self.post("questions", self.question_payload())
        self.assertEqual(result.status_code, 201, result.content)
        pk = result.json()["id"]
        self.assertEqual(
            self.client.get("/api/v1/questions?subject=SE&topic=Testing&difficulty=HARD").json()["count"], 1
        )
        self.assertEqual(self.client.get("/api/v1/questions?difficulty=UNKNOWN").status_code, 400)
        self.assertEqual(
            self.client.patch("/api/v1/questions/" + pk, {"text": "Changed"}, format="json").status_code, 200
        )
        self.assertEqual(self.client.delete("/api/v1/questions/" + pk).status_code, 204)
        self.assertEqual(
            list(AuditLog.objects.filter(target=pk).order_by("id").values_list("action", flat=True)),
            ["QUESTION_CREATED", "QUESTION_UPDATED", "QUESTION_DELETED"],
        )

    def test_question_option_and_marks_validation(self):
        self.login()
        cases = [
            {"options": [{"text": "Only", "is_correct": True}]},
            {"options": [{"text": "A"}, {"text": "B"}]},
            {"options": [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": True}]},
            {"options": [{"text": "Same", "is_correct": True}, {"text": "same"}]},
            {"default_marks": "0"},
            {"negative_marks": "-1"},
            {"difficulty": "BAD"},
        ]
        for changes in cases:
            data = self.question_payload()
            data.update(changes)
            self.assertEqual(self.post("questions", data).status_code, 400, data)

    def test_partial_options_require_text_and_replace_atomically(self):
        self.login()
        url = f"/api/v1/questions/{self.questions[0].id}"
        self.assertEqual(
            self.client.patch(
                url, {"options": [{"is_correct": True}, {"is_correct": False}]}, format="json"
            ).status_code,
            400,
        )
        self.assertEqual(self.questions[0].options.count(), 2)
        result = self.client.patch(
            url,
            {"options": [{"text": "New right", "is_correct": True}, {"text": "New wrong"}]},
            format="json",
        )
        self.assertEqual(result.status_code, 200, result.content)
        self.assertEqual(self.questions[0].options.filter(is_correct=True).get().text, "New right")

    def test_in_use_question_cannot_change_or_delete(self):
        self.login()
        self.select(mode="manual", question_ids=[str(self.questions[0].id)])
        url = f"/api/v1/questions/{self.questions[0].id}"
        self.assertEqual(self.client.patch(url, {"default_marks": "5"}, format="json").status_code, 409)
        self.assertEqual(self.client.delete(url).status_code, 409)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.total_marks, 2)

    def test_injection_strings_remain_data(self):
        self.login()
        payload = self.question_payload()
        payload["text"] = "<script>alert(1)</script>'; DROP TABLE users; --"
        result = self.post("questions", payload)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json()["text"], payload["text"])
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(self.client.get("/api/v1/questions?subject=%27%20OR%201%3D1").json()["count"], 0)

    def test_manual_selection_order_and_totals(self):
        self.login()
        ids = [str(self.questions[2].id), str(self.questions[0].id)]
        result = self.select(mode="manual", question_ids=ids)
        self.assertEqual(result.status_code, 200, result.content)
        self.assertEqual(result.json()["total_marks"], "4.00")
        self.assertEqual([str(x.question_id) for x in ExamQuestion.objects.filter(exam=self.exam)], ids)
        self.assertEqual(len(self.client.get(f"/api/v1/exams/{self.exam.id}/questions").json()["results"]), 2)

    def test_selection_failure_preserves_existing_exam(self):
        self.login()
        self.select(mode="manual", question_ids=[str(self.questions[0].id)])
        invalid = [
            dict(mode="manual", question_ids=[str(uuid.uuid4())]),
            dict(mode="manual", question_ids=[str(self.questions[0].id)] * 2),
            dict(mode="random", random_count=20),
            dict(mode="random", random_count=2, difficulty_mix={"HARD": 2}),
            dict(mode="random", random_count=2, difficulty_mix={"EASY": 1}),
            dict(mode="random", random_count=1, difficulty_mix={"BAD": 1}),
        ]
        for payload in invalid:
            self.assertEqual(self.select(**payload).status_code, 400, payload)
            self.assertEqual(self.exam.questions.count(), 1)
            self.exam.refresh_from_db()
            self.assertEqual(self.exam.total_marks, 2)

    def test_random_selection_without_replacement_and_mix(self):
        self.login()
        result = self.select(
            mode="random",
            random_count=3,
            subject="SE",
            topic="Testing",
            difficulty_mix={"EASY": 2, "HARD": 1},
        )
        self.assertEqual(result.status_code, 200, result.content)
        self.assertEqual(self.exam.questions.filter(difficulty="EASY").count(), 2)
        self.assertEqual(self.exam.questions.filter(difficulty="HARD").count(), 1)
        self.assertEqual(result.json()["total_marks"], "6.00")
        self.assertEqual(self.select(mode="random", random_count=4).status_code, 200)
        self.assertEqual(self.exam.questions.count(), 4)

    def test_exam_create_validation_and_readonly_total(self):
        self.login()
        now = timezone.now()
        data = dict(
            title="New",
            duration_minutes=30,
            start_time=(now + timedelta(hours=1)).isoformat(),
            end_time=(now + timedelta(hours=2)).isoformat(),
            result_visible_from=(now + timedelta(hours=3)).isoformat(),
            total_marks=999,
        )
        result = self.post("exams", data)
        self.assertEqual(result.status_code, 201, result.content)
        self.assertEqual(result.json()["total_marks"], "0.00")
        for changes in (
            {"duration_minutes": 0},
            {"end_time": data["start_time"]},
            {"start_time": (now - timedelta(hours=1)).isoformat()},
        ):
            self.assertEqual(self.post("exams", dict(data, **changes)).status_code, 400)

    def test_exam_partial_updates_validate_existing_schedule(self):
        self.login()
        url = f"/api/v1/exams/{self.exam.id}"
        self.assertEqual(self.client.patch(url, {"title": "Updated"}, format="json").status_code, 200)
        self.assertEqual(
            self.client.patch(
                url, {"end_time": (self.exam.start_time - timedelta(minutes=1)).isoformat()}, format="json"
            ).status_code,
            400,
        )

    def test_started_exam_freezes_all_configuration(self):
        self.login()
        Exam.objects.filter(pk=self.exam.id).update(start_time=timezone.now() - timedelta(minutes=1))
        self.assertEqual(
            self.client.patch(
                f"/api/v1/exams/{self.exam.id}", {"title": "Changed"}, format="json"
            ).status_code,
            400,
        )
        self.assertEqual(
            self.select(mode="manual", question_ids=[str(self.questions[0].id)]).status_code, 400
        )
        self.assertEqual(
            self.post(f"exams/{self.exam.id}/batches", {"batch_ids": [str(self.batch.id)]}).status_code, 400
        )

    def test_batch_assignment_replacement_and_invalid_atomicity(self):
        self.login()
        url = f"exams/{self.exam.id}/batches"
        self.assertEqual(
            self.post(url, {"batch_ids": [str(self.batch.id), str(self.batch.id)]}).json()[
                "batches_assigned"
            ],
            1,
        )
        self.assertEqual(self.post(url, {"batch_ids": [str(uuid.uuid4())]}).status_code, 400)
        self.assertEqual(list(self.exam.batches.all()), [self.batch])
        self.assertEqual(self.post(url, {"batch_ids": [str(self.batch2.id)]}).status_code, 200)
        self.assertEqual(list(self.exam.batches.all()), [self.batch2])

    def test_available_exams_membership_time_boundaries_and_no_keys(self):
        self.login()
        self.select(mode="manual", question_ids=[str(self.questions[0].id)])
        self.post(f"exams/{self.exam.id}/batches", {"batch_ids": [str(self.batch.id)]})
        self.login(self.student)
        for instant, expected in (
            (self.exam.start_time - timedelta(seconds=1), 0),
            (self.exam.start_time, 1),
            (self.exam.end_time - timedelta(seconds=1), 1),
            (self.exam.end_time, 0),
        ):
            with patch("portal.views.timezone.now", return_value=instant):
                result = self.client.get("/api/v1/exams/available")
                self.assertEqual(len(result.json()["results"]), expected)
                self.assertNotIn("is_correct", result.content.decode())
                self.assertNotIn("options", result.content.decode())
        self.login(self.other)
        with patch("portal.views.timezone.now", return_value=self.exam.start_time):
            self.assertEqual(self.client.get("/api/v1/exams/available").json()["results"], [])

    def test_available_exams_deduplicates_membership_and_hides_empty(self):
        StudentBatch.objects.create(student=self.student, batch=self.batch2)
        ExamBatch.objects.bulk_create(
            [ExamBatch(exam=self.exam, batch=self.batch), ExamBatch(exam=self.exam, batch=self.batch2)]
        )
        self.login(self.student)
        with patch("portal.views.timezone.now", return_value=self.exam.start_time):
            self.assertEqual(self.client.get("/api/v1/exams/available").json()["results"], [])
            ExamQuestion.objects.create(exam=self.exam, question=self.questions[0], sequence=1)
            Exam.objects.filter(pk=self.exam.pk).update(total_marks=2)
            self.assertEqual(len(self.client.get("/api/v1/exams/available").json()["results"]), 1)

    def test_audit_is_immutable_in_orm_and_database(self):
        entry = AuditLog.objects.create(actor=self.admin, action="TEST", target="test")
        for action in (
            lambda: entry.save(),
            lambda: entry.delete(),
            lambda: AuditLog.objects.update(action="BAD"),
            lambda: AuditLog.objects.all().delete(),
        ):
            with self.assertRaises(ValueError):
                action()
        for sql in (
            "UPDATE audit_logs SET action=%s WHERE id=%s",
            "DELETE FROM audit_logs WHERE action=%s AND id=%s",
        ):
            with self.assertRaises(DatabaseError), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(sql, ["TEST", entry.pk])
        self.assertTrue(AuditLog.objects.filter(pk=entry.pk).exists())

    def test_composite_keys_and_email_uniqueness(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            StudentBatch.objects.create(student=self.student, batch=self.batch)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create(username="duplicate", email="STUDENT@example.test")
        with connection.cursor() as cursor:
            for table, columns in [
                ("student_batches", {"student_id", "batch_id"}),
                ("exam_questions", {"exam_id", "question_id"}),
                ("exam_batches", {"exam_id", "batch_id"}),
            ]:
                constraints = connection.introspection.get_constraints(cursor, table)
                primary = [set(c["columns"]) for c in constraints.values() if c["primary_key"]]
                self.assertEqual(primary, [columns])

    def create_student_attempt(self):
        self.login()
        selected = self.select(mode="manual", question_ids=[str(self.questions[0].id)])
        self.assertEqual(selected.status_code, 200, selected.content)
        assigned = self.post(f"exams/{self.exam.id}/batches", {"batch_ids": [str(self.batch.id)]})
        self.assertEqual(assigned.status_code, 200, assigned.content)
        now = timezone.now()
        Exam.objects.filter(pk=self.exam.id).update(
            start_time=now - timedelta(minutes=1), end_time=now + timedelta(hours=1)
        )
        logged_in = self.login(self.student)
        self.assertEqual(logged_in.status_code, 200, logged_in.content)
        session_id = uuid.uuid4()
        self.student_access_header = "Bearer " + logged_in.json()["access_token"]
        self.client.credentials(
            HTTP_X_CSRFTOKEN=self.csrf,
            HTTP_AUTHORIZATION=self.student_access_header,
            HTTP_X_EXAM_SESSION=str(session_id),
        )
        result = self.post(f"exams/{self.exam.id}/attempt", {"session_id": str(session_id)})
        return result, session_id

    def test_attempt_starts_once_and_blocks_a_second_session(self):
        result, session_id = self.create_student_attempt()
        self.assertEqual(result.status_code, 201, result.content)
        data = result.json()
        self.assertEqual(data["status"], ExamAttempt.IN_PROGRESS)
        self.assertNotIn("is_correct", result.content.decode())
        self.assertNotIn("correct_option", result.content.decode())
        resumed = self.post(f"exams/{self.exam.id}/attempt", {"session_id": str(session_id)})
        self.assertEqual(resumed.status_code, 200, resumed.content)
        self.assertEqual(ExamAttempt.objects.filter(exam=self.exam, student=self.student).count(), 1)
        other_session = uuid.uuid4()
        self.client.credentials(
            HTTP_X_CSRFTOKEN=self.csrf,
            HTTP_AUTHORIZATION=self.student_access_header,
            HTTP_X_EXAM_SESSION=str(other_session),
        )
        rejected = self.post(f"exams/{self.exam.id}/attempt", {"session_id": str(other_session)})
        self.assertEqual(rejected.status_code, 409)

    def test_attempt_answers_autosave_and_recover_after_refresh(self):
        result, session_id = self.create_student_attempt()
        self.assertEqual(result.status_code, 201, result.content)
        data = result.json()
        question = data["questions"][0]
        option_id = question["options"][0]["id"]
        saved = self.client.patch(
            f"/api/v1/attempts/{data['attempt_id']}/answers",
            {"question_id": question["id"], "option_id": option_id},
            format="json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        answer = AttemptAnswer.objects.get(attempt_id=data["attempt_id"], question_id=question["id"])
        self.assertEqual(str(answer.selected_option_id), option_id)
        restored = self.client.get(f"/api/v1/attempts/{data['attempt_id']}")
        self.assertEqual(restored.status_code, 200, restored.content)
        self.assertEqual(restored.json()["answers"][question["id"]], option_id)
        self.assertEqual(restored.json()["questions"][0]["selected_option_id"], option_id)
        self.assertNotIn("is_correct", restored.content.decode())

    def test_attempt_rejects_foreign_options_and_late_writes(self):
        result, _ = self.create_student_attempt()
        self.assertEqual(result.status_code, 201, result.content)
        data = result.json()
        foreign_question = self.questions[1]
        foreign_option = str(foreign_question.options.first().id)
        rejected = self.client.patch(
            f"/api/v1/attempts/{data['attempt_id']}/answers",
            {"question_id": data["questions"][0]["id"], "option_id": foreign_option},
            format="json",
        )
        self.assertEqual(rejected.status_code, 400)
        ExamAttempt.objects.filter(pk=data["attempt_id"]).update(
            deadline_at=timezone.now() - timedelta(seconds=1)
        )
        late = self.client.patch(
            f"/api/v1/attempts/{data['attempt_id']}/answers",
            {"question_id": data["questions"][0]["id"], "option_id": None},
            format="json",
        )
        self.assertEqual(late.status_code, 409)
        self.assertEqual(
            ExamAttempt.objects.get(pk=data["attempt_id"]).status,
            ExamAttempt.AUTO_SUBMITTED,
        )
        expired = self.client.get(f"/api/v1/attempts/{data['attempt_id']}")
        self.assertEqual(expired.status_code, 200, expired.content)
        self.assertEqual(expired.json()["status"], ExamAttempt.AUTO_SUBMITTED)

    def test_expiry_worker_auto_submits_without_browser_request(self):
        result, _ = self.create_student_attempt()
        self.assertEqual(result.status_code, 201, result.content)
        attempt_id = result.json()["attempt_id"]
        ExamAttempt.objects.filter(pk=attempt_id).update(deadline_at=timezone.now() - timedelta(seconds=1))
        call_command("expire_exam_attempts")
        attempt = ExamAttempt.objects.get(pk=attempt_id)
        self.assertEqual(attempt.status, ExamAttempt.AUTO_SUBMITTED)
        self.assertIsNotNone(attempt.submitted_at)
        self.assertEqual(
            AuditLog.objects.filter(action="EXAM_ATTEMPT_AUTO_SUBMITTED", target=attempt_id).count(),
            1,
        )

    def test_manual_submission_is_idempotent(self):
        result, _ = self.create_student_attempt()
        self.assertEqual(result.status_code, 201, result.content)
        attempt_id = result.json()["attempt_id"]
        first = self.client.post(f"/api/v1/attempts/{attempt_id}/submit", {}, format="json")
        second = self.client.post(f"/api/v1/attempts/{attempt_id}/submit", {}, format="json")
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(second.json()["status"], ExamAttempt.SUBMITTED)
        self.assertEqual(
            AuditLog.objects.filter(action="EXAM_ATTEMPT_SUBMITTED", target=attempt_id).count(), 1
        )

    def test_terminal_attempts_preserve_saved_answers_and_timestamps(self):
        result, _ = self.create_student_attempt()
        data = result.json()
        question = data["questions"][0]
        url = f"/api/v1/attempts/{data['attempt_id']}/answers"
        self.assertEqual(
            self.client.patch(
                url, {"question_id": question["id"], "option_id": question["options"][0]["id"]}, format="json"
            ).status_code,
            200,
        )
        before = AttemptAnswer.objects.get(attempt_id=data["attempt_id"])
        saved_at = ExamAttempt.objects.get(pk=data["attempt_id"]).last_saved_at
        for terminal in (ExamAttempt.SUBMITTED, ExamAttempt.AUTO_SUBMITTED, ExamAttempt.DISQUALIFIED):
            with self.subTest(status=terminal):
                ExamAttempt.objects.filter(pk=data["attempt_id"]).update(status=terminal)
                for option in (None, question["options"][1]["id"]):
                    rejected = self.client.patch(
                        url, {"question_id": question["id"], "option_id": option}, format="json"
                    )
                    self.assertEqual(rejected.status_code, 409, rejected.content)
                after = AttemptAnswer.objects.get(pk=before.pk)
                self.assertEqual(after.selected_option_id, before.selected_option_id)
                self.assertEqual(after.saved_at, before.saved_at)
                attempt = ExamAttempt.objects.get(pk=data["attempt_id"])
                self.assertEqual(attempt.last_saved_at, saved_at)
                self.assertEqual(attempt.status, terminal)

    def test_attempt_write_routes_reject_other_students_and_admins(self):
        result, session = self.create_student_attempt()
        data = result.json()
        for user, expected in ((self.other, 404), (self.admin, 403)):
            with self.subTest(role=user.role):
                login = self.login(user)
                self.client.credentials(
                    HTTP_X_CSRFTOKEN=self.csrf,
                    HTTP_AUTHORIZATION="Bearer " + login.json()["access_token"],
                    HTTP_X_EXAM_SESSION=str(session),
                )
                rejected = self.client.patch(
                    f"/api/v1/attempts/{data['attempt_id']}/answers",
                    {
                        "question_id": data["questions"][0]["id"],
                        "option_id": None,
                    },
                    format="json",
                )
                self.assertEqual(rejected.status_code, expected, rejected.content)
                rejected = self.client.post(
                    f"/api/v1/attempts/{data['attempt_id']}/submit", {}, format="json"
                )
                self.assertEqual(rejected.status_code, expected, rejected.content)
        self.assertFalse(AttemptAnswer.objects.filter(attempt_id=data["attempt_id"]).exists())
        self.assertEqual(ExamAttempt.objects.get(pk=data["attempt_id"]).status, ExamAttempt.IN_PROGRESS)

    def test_disqualified_attempt_cannot_be_reopened_by_student(self):
        result, session = self.create_student_attempt()
        pk = result.json()["attempt_id"]
        ExamAttempt.objects.filter(pk=pk).update(status=ExamAttempt.DISQUALIFIED)
        resumed = self.post(f"exams/{self.exam.id}/attempt", {"session_id": str(session)})
        self.assertEqual(resumed.json()["status"], ExamAttempt.DISQUALIFIED)
        submitted = self.client.post(f"/api/v1/attempts/{pk}/submit", {}, format="json")
        self.assertEqual(submitted.json()["status"], ExamAttempt.DISQUALIFIED)
        self.assertFalse(AuditLog.objects.filter(action="EXAM_ATTEMPT_SUBMITTED", target=pk).exists())

    def test_readiness_endpoint(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})

    @override_settings(REFRESH_COOKIE_SECURE=True)
    def test_deployment_refresh_cookie_is_secure(self):
        response = self.login()
        cookie = response.cookies["oep_refresh"]
        self.assertTrue(cookie["secure"])
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["path"], "/api/v1/auth")

    def test_import_row_limit_is_enforced_before_writes(self):
        self.login()
        data = "name,email,usn,batch\n" + "\n".join(f"Name,s{i}@example.test,S{i},CSE-A" for i in range(1001))
        self.assertEqual(self.upload_csv(data).status_code, 400)
        self.assertEqual(User.objects.count(), 3)
