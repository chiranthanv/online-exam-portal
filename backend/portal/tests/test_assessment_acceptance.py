import csv
from datetime import timedelta
from io import StringIO

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import (
    AttemptAnswer,
    AuditLog,
    Exam,
    ExamAttempt,
    ExamQuestion,
    Option,
    ProctoringEvent,
    Question,
    User,
)


class AssessmentAcceptanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="accept-admin",
            email="accept-admin@example.test",
            name="Faculty",
            role="ADMIN",
            password="Test-Password-123!",
        )
        cls.students = [
            User.objects.create_user(
                username=f"accept-student-{i}",
                email=f"accept-{i}@example.test",
                name=f"Student {i}",
                usn=f"ACCEPT-{i:03}",
                password="Test-Password-123!",
            )
            for i in range(1, 4)
        ]
        cls.questions = []
        for i, (marks, penalty) in enumerate([("2.00", "0.50"), ("3.00", "1.00")], 1):
            question = Question.objects.create(
                text=f"Question {i}",
                subject="Math",
                topic="Arithmetic",
                difficulty="EASY" if i == 1 else "MEDIUM",
                default_marks=marks,
                negative_marks=penalty,
                created_by=cls.admin,
            )
            Option.objects.create(question=question, text="Correct", is_correct=True)
            Option.objects.create(question=question, text="Wrong", is_correct=False)
            cls.questions.append(question)
        now = timezone.now()
        cls.exam = Exam.objects.create(
            title="Report acceptance exam",
            duration_minutes=30,
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            result_visible_from=now - timedelta(minutes=1),
            total_marks="5.00",
            created_by=cls.admin,
        )
        for seq, question in enumerate(cls.questions, 1):
            ExamQuestion.objects.create(exam=cls.exam, question=question, sequence=seq)

    def make_attempt(self, student, status=ExamAttempt.SUBMITTED, selected=None, evaluated=True):
        now = timezone.now()
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            student=student,
            status=status,
            deadline_at=now + timedelta(minutes=5),
            submitted_at=now,
            score="1.00" if evaluated else None,
            evaluated_at=now if evaluated else None,
        )
        for question, option in selected or []:
            AttemptAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option_id=option.id if option else None,
            )
        return attempt

    def admin_client(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        return client

    def test_class_and_question_reports_match_csv_and_pdf_exports(self):
        correct = self.questions[0].options.get(is_correct=True)
        wrong = self.questions[0].options.get(is_correct=False)
        self.make_attempt(self.students[0], selected=[(self.questions[0], correct)])
        self.make_attempt(self.students[1], selected=[(self.questions[0], wrong)])
        self.make_attempt(self.students[2])
        disqualified_student = User.objects.create_user(
            username="accept-disqualified",
            email="accept-disqualified@example.test",
            name="Disqualified Student",
            usn="ACCEPT-004",
            password="Test-Password-123!",
        )
        self.make_attempt(
            disqualified_student,
            status=ExamAttempt.DISQUALIFIED,
            selected=[(self.questions[0], correct)],
        )
        client = self.admin_client()
        class_json = client.get(f"/api/v1/reports/class?exam_id={self.exam.id}")
        class_csv = client.get(f"/api/v1/reports/class?exam_id={self.exam.id}&export=csv")
        class_pdf = client.get(f"/api/v1/reports/class?exam_id={self.exam.id}&export=pdf")
        self.assertEqual(class_json.status_code, 200)
        self.assertEqual(class_csv.status_code, 200)
        self.assertTrue(class_pdf.content.startswith(b"%PDF"))
        class_rows = list(csv.DictReader(StringIO(class_csv.content.decode())))
        self.assertEqual(len(class_rows), len(class_json.data["results"]))
        question_json = client.get(f"/api/v1/reports/questions?exam_id={self.exam.id}")
        question_csv = client.get(f"/api/v1/reports/questions?exam_id={self.exam.id}&export=csv")
        question_pdf = client.get(f"/api/v1/reports/questions?exam_id={self.exam.id}&export=pdf")
        self.assertEqual(question_json.status_code, 200)
        self.assertEqual(question_csv.status_code, 200)
        self.assertTrue(question_pdf.content.startswith(b"%PDF"))
        parsed = list(csv.DictReader(StringIO(question_csv.content.decode())))
        self.assertEqual(parsed[0]["correct"], str(question_json.data["results"][0]["correct"]))
        row = question_json.data["results"][0]
        self.assertEqual(
            (row["submitted_attempts"], row["correct"], row["incorrect"], row["unanswered"]),
            (3, 1, 1, 1),
        )

    def test_csv_exports_neutralize_formula_prefixes_only_in_text_columns(self):
        student = self.students[0]
        student.name = '=HYPERLINK("https://example.test","open")'
        student.usn = "+SUM(1,1)"
        student.save(update_fields=["name", "usn"])
        self.make_attempt(student)

        question = self.questions[0]
        question.difficulty = "-cmd"
        question.subject = "@SUM(1,1)"
        question.topic = " =1+1"
        question.save(update_fields=["difficulty", "subject", "topic"])

        client = self.admin_client()
        class_csv = client.get(f"/api/v1/reports/class?exam_id={self.exam.id}&export=csv")
        self.assertEqual(class_csv.status_code, 200)
        class_row = next(
            row
            for row in csv.DictReader(StringIO(class_csv.content.decode()))
            if row["student_id"] == str(student.id)
        )
        self.assertEqual(class_row["student_name"], '\'=HYPERLINK("https://example.test","open")')
        self.assertEqual(class_row["usn"], "'+SUM(1,1)")
        self.assertEqual(class_row["score"], "1.00")

        question_csv = client.get(f"/api/v1/reports/questions?exam_id={self.exam.id}&export=csv")
        self.assertEqual(question_csv.status_code, 200)
        question_row = next(iter(csv.DictReader(StringIO(question_csv.content.decode()))))
        self.assertEqual(question_row["difficulty"], "'-cmd")
        self.assertEqual(question_row["subject"], "'@SUM(1,1)")
        self.assertEqual(question_row["topic"], "' =1+1")
        self.assertEqual(question_row["submitted_attempts"], "1")
        self.assertEqual(question_row["correct"], "0")

    def test_reports_are_admin_only_and_hidden_until_release(self):
        client = APIClient()
        client.force_authenticate(self.students[0])
        denied = client.get(f"/api/v1/reports/class?exam_id={self.exam.id}")
        self.assertEqual(denied.status_code, 403)
        self.exam.result_visible_from = timezone.now() + timedelta(hours=1)
        self.exam.save(update_fields=["result_visible_from"])
        admin = self.admin_client()
        hidden = admin.get(f"/api/v1/reports/class?exam_id={self.exam.id}")
        self.assertEqual(hidden.status_code, 400)

    def test_student_result_requires_evaluation_and_release(self):
        pending = self.make_attempt(self.students[0], evaluated=False)
        client = APIClient()
        client.force_authenticate(self.students[0])
        response = client.get(f"/api/v1/attempts/{pending.id}/result")
        self.assertEqual(response.status_code, 409)
        pending.evaluated_at = timezone.now()
        pending.score = "1.00"
        pending.save(update_fields=["evaluated_at", "score"])
        self.exam.result_visible_from = timezone.now() + timedelta(hours=1)
        self.exam.save(update_fields=["result_visible_from"])
        hidden = client.get(f"/api/v1/attempts/{pending.id}/result")
        self.assertEqual(hidden.status_code, 403)
        self.assertNotIn("score", hidden.data)

    def test_student_payload_does_not_expose_correct_option_flags(self):
        from portal.views import _attempt_payload

        attempt = self.make_attempt(self.students[0])
        payload = _attempt_payload(attempt)
        client = APIClient()
        client.force_authenticate(self.students[0])
        response = client.get(
            f"/api/v1/attempts/{attempt.id}",
            HTTP_X_EXAM_SESSION=str(attempt.session_key),
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("score", response.data)
        self.assertNotIn("is_correct", str(response.data))
        self.assertNotIn("is_correct", str(payload))
        self.assertTrue(
            all(set(option) == {"id", "text"} for q in payload["questions"] for option in q["options"])
        )

    def test_each_tab_switch_and_blur_is_visible_in_admin_review(self):
        attempt = self.make_attempt(self.students[0], status=ExamAttempt.IN_PROGRESS)
        client = APIClient()
        client.force_authenticate(self.students[0])
        endpoint = f"/api/v1/attempts/{attempt.id}/proctoring-events"
        for kind in [ProctoringEvent.TAB_SWITCH, ProctoringEvent.TAB_SWITCH, ProctoringEvent.WINDOW_BLUR]:
            response = client.post(
                endpoint,
                {"event_type": kind},
                format="json",
                HTTP_X_EXAM_SESSION=str(attempt.session_key),
            )
            self.assertEqual(response.status_code, 201)
        response = self.admin_client().get(f"/api/v1/admin/attempts?exam_id={self.exam.id}")
        self.assertEqual(len(response.data["results"][0]["flags"]), 3)

    def test_repermit_restores_auto_submitted_status_and_records_actor(self):
        attempt = self.make_attempt(self.students[0], status=ExamAttempt.AUTO_SUBMITTED)
        client = self.admin_client()
        url = f"/api/v1/admin/attempts/{attempt.id}/override"
        changed = client.post(url, {"disqualified": True, "reason": "Review evidence"}, format="json")
        self.assertEqual(changed.status_code, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status_before_disqualification, ExamAttempt.AUTO_SUBMITTED)
        restored = client.post(url, {"disqualified": False, "reason": ""}, format="json")
        self.assertEqual(restored.status_code, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.AUTO_SUBMITTED)
        audit = AuditLog.objects.filter(target=str(attempt.id)).latest("timestamp")
        self.assertEqual(audit.actor, self.admin)
        self.assertEqual(audit.action, "ATTEMPT_REPERMITTED")

    def test_disqualified_result_and_report_are_hidden_until_repermitted(self):
        attempt = self.make_attempt(self.students[0], status=ExamAttempt.SUBMITTED)
        admin = self.admin_client()
        override_url = f"/api/v1/admin/attempts/{attempt.id}/override"
        disqualified = admin.post(
            override_url,
            {"disqualified": True, "reason": "Admin review pending"},
            format="json",
        )
        self.assertEqual(disqualified.status_code, 200)
        student = APIClient()
        student.force_authenticate(self.students[0])
        hidden_result = student.get(f"/api/v1/attempts/{attempt.id}/result")
        self.assertEqual(hidden_result.status_code, 403)
        hidden_report = admin.get(f"/api/v1/reports/class?exam_id={self.exam.id}")
        self.assertNotIn(
            str(attempt.id),
            {row["attempt_id"] for row in hidden_report.data["results"]},
        )

        restored = admin.post(
            override_url,
            {"disqualified": False, "reason": ""},
            format="json",
        )
        self.assertEqual(restored.status_code, 200)
        visible_result = student.get(f"/api/v1/attempts/{attempt.id}/result")
        self.assertEqual(visible_result.status_code, 200)
        visible_report = admin.get(f"/api/v1/reports/class?exam_id={self.exam.id}")
        self.assertIn(
            str(attempt.id),
            {row["attempt_id"] for row in visible_report.data["results"]},
        )
