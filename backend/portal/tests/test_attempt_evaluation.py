"""Acceptance tests for server-side evaluation, result release and proctoring APIs."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import (
    Attempt,
    AuditLog,
    Batch,
    Exam,
    ExamBatch,
    ExamQuestion,
    Option,
    ProctoringFlag,
    Question,
    StudentBatch,
    User,
)


class AttemptEvaluationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="attempt-admin",
            email="attempt-admin@example.test",
            name="Attempt Admin",
            role="ADMIN",
            password="Test-Only-Passphrase-491!",
        )
        cls.student = User.objects.create_user(
            username="attempt-student",
            email="attempt-student@example.test",
            name="Attempt Student",
            usn="ATT-001",
            role="STUDENT",
            password="Test-Only-Passphrase-491!",
        )
        cls.batch = Batch.objects.create(name="ATTEMPT-TEST", year=2026)
        StudentBatch.objects.create(student=cls.student, batch=cls.batch)
        cls.questions = []
        cls.options = []
        for index, correct_text in enumerate(("A right", "B right")):
            question = Question.objects.create(
                text=f"Question {index + 1}",
                subject="SE",
                topic="Evaluation",
                difficulty="EASY",
                default_marks="2.00",
                negative_marks="0.50",
                created_by=cls.admin,
            )
            correct = Option.objects.create(question=question, text=correct_text, is_correct=True)
            wrong = Option.objects.create(question=question, text=f"Wrong {index + 1}", is_correct=False)
            cls.questions.append(question)
            cls.options.append((correct, wrong))
        now = timezone.now()
        cls.exam = Exam.objects.create(
            title="Evaluation test",
            duration_minutes=30,
            start_time=now - timedelta(minutes=1),
            end_time=now + timedelta(minutes=29),
            result_visible_from=now + timedelta(hours=1),
            total_marks="4.00",
            created_by=cls.admin,
        )
        for sequence, question in enumerate(cls.questions, 1):
            ExamQuestion.objects.create(exam=cls.exam, question=question, sequence=sequence)
        ExamBatch.objects.create(exam=cls.exam, batch=cls.batch)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    def start(self):
        response = self.client.post(f"/api/v1/exams/{self.exam.id}/attempt", {}, format="json")
        self.assertIn(response.status_code, (200, 201), response.content)
        return response.json()

    def test_attempt_questions_never_include_correct_flags_and_score_is_server_computed(self):
        started = self.start()
        self.assertEqual(len(started["questions"]), 2)
        self.assertNotIn("is_correct", str(started["questions"]))
        attempt_id = started["attempt_id"]
        response = self.client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
            {
                "answers": [
                    {"question_id": str(self.questions[0].id), "option_id": str(self.options[0][0].id)},
                    {"question_id": str(self.questions[1].id), "option_id": str(self.options[1][1].id)},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotIn("score", response.json())
        self.assertEqual(str(Attempt.objects.get(pk=started["attempt_id"]).score), "1.50")
        self.assertEqual(Attempt.objects.get(pk=attempt_id).answers.count(), 2)

    def test_unanswered_questions_score_zero_and_duplicate_submit_is_idempotent(self):
        started = self.start()
        attempt_id = started["attempt_id"]
        payload = {
            "answers": [{"question_id": str(self.questions[0].id), "option_id": str(self.options[0][0].id)}]
        }
        first = self.client.post(f"/api/v1/attempts/{attempt_id}/submit", payload, format="json")
        second = self.client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
            {
                "answers": [
                    {"question_id": str(self.questions[1].id), "option_id": str(self.options[1][0].id)}
                ]
            },
            format="json",
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertNotIn("score", first.json())
        self.assertNotIn("score", second.json())
        self.assertEqual(str(Attempt.objects.get(pk=started["attempt_id"]).score), "2.00")
        self.assertEqual(Attempt.objects.get(pk=attempt_id).answers.count(), 2)

    def test_negative_total_is_clamped_to_zero(self):
        started = self.start()
        response = self.client.post(
            f"/api/v1/attempts/{started['attempt_id']}/submit",
            {
                "answers": [
                    {"question_id": str(self.questions[0].id), "option_id": str(self.options[0][1].id)},
                    {"question_id": str(self.questions[1].id), "option_id": str(self.options[1][1].id)},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(str(Attempt.objects.get(pk=started["attempt_id"]).score), "0.00")
        self.assertNotIn("score", response.json())

    def test_results_hidden_until_release_and_admin_override_is_audited(self):
        attempt_id = self.start()["attempt_id"]
        submitted = self.client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
            {"answers": []},
            format="json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        result_url = f"/api/v1/attempts/{attempt_id}/result"
        self.assertEqual(self.client.get(result_url).status_code, 403)
        self.exam.result_visible_from = timezone.now() - timedelta(seconds=1)
        self.exam.save(update_fields=["result_visible_from"])
        self.assertEqual(self.client.get(result_url).status_code, 200)

        admin_client = APIClient()
        admin_client.force_authenticate(user=self.admin)
        response = admin_client.post(
            f"/api/v1/admin/attempts/{attempt_id}/override",
            {"disqualified": True, "reason": "Reviewed suspicious behavior"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.client.get(result_url).status_code, 403)
        response = admin_client.post(
            f"/api/v1/admin/attempts/{attempt_id}/override",
            {"disqualified": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.client.get(result_url).status_code, 200)
        self.assertEqual(
            list(
                AuditLog.objects.filter(target=attempt_id)
                .order_by("timestamp")
                .values_list("action", flat=True)
            ),
            ["ATTEMPT_STARTED", "ATTEMPT_SUBMITTED", "ATTEMPT_DISQUALIFIED", "ATTEMPT_REPERMITTED"],
        )

    def test_proctoring_events_are_individual_and_admin_can_review_them(self):
        attempt_id = self.start()["attempt_id"]
        for event in ("TAB_SWITCH", "WINDOW_BLUR", "TAB_SWITCH"):
            response = self.client.post(
                f"/api/v1/attempts/{attempt_id}/proctoring-events",
                {"event_type": event},
                format="json",
            )
            self.assertEqual(response.status_code, 201, response.content)
        admin_client = APIClient()
        admin_client.force_authenticate(user=self.admin)
        response = admin_client.get("/api/v1/admin/attempts")
        self.assertEqual(response.status_code, 200, response.content)
        attempt = response.json()["results"][0]
        self.assertEqual(
            [x["event_type"] for x in attempt["flags"]], ["TAB_SWITCH", "WINDOW_BLUR", "TAB_SWITCH"]
        )
        flag = ProctoringFlag.objects.first()
        with self.assertRaises(ValueError):
            flag.delete()
        with self.assertRaises(ValueError):
            ProctoringFlag.objects.filter(pk=flag.pk).update(event_type="WINDOW_BLUR")

    def test_invalid_cross_question_option_and_duplicate_question_rejected(self):
        attempt_id = self.start()["attempt_id"]
        response = self.client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
            {
                "answers": [
                    {"question_id": str(self.questions[0].id), "option_id": str(self.options[1][0].id)}
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Attempt.objects.get(pk=attempt_id).submitted_at)
        response = self.client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
            {
                "answers": [
                    {"question_id": str(self.questions[0].id), "option_id": str(self.options[0][0].id)},
                    {"question_id": str(self.questions[0].id), "option_id": str(self.options[0][1].id)},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reports_require_release_exclude_disqualified_and_export_csv(self):
        attempt_id = self.start()["attempt_id"]
        response = self.client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
            {
                "answers": [
                    {"question_id": str(self.questions[0].id), "option_id": str(self.options[0][0].id)}
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        admin_client = APIClient()
        admin_client.force_authenticate(user=self.admin)
        class_url = f"/api/v1/admin/reports/class?exam_id={self.exam.id}"
        question_url = f"/api/v1/admin/reports/questions?exam_id={self.exam.id}"
        self.assertEqual(admin_client.get(class_url).status_code, 400)
        self.exam.result_visible_from = timezone.now() - timedelta(seconds=1)
        self.exam.save(update_fields=["result_visible_from"])
        class_json = admin_client.get(class_url)
        self.assertEqual(class_json.status_code, 200, class_json.content)
        self.assertEqual(class_json.json()["results"][0]["score"], "2.00")
        class_csv = admin_client.get(class_url + "&export=csv")
        self.assertEqual(class_csv.status_code, 200)
        self.assertIn("student_name,usn,score,total_marks", class_csv.content.decode())
        class_pdf = admin_client.get(class_url + "&export=pdf")
        self.assertEqual(class_pdf.status_code, 200)
        self.assertEqual(class_pdf["Content-Type"], "application/pdf")
        self.assertTrue(class_pdf.content[:4] == bytes([37, 80, 68, 70]))
        question_json = admin_client.get(question_url)
        self.assertEqual(question_json.status_code, 200, question_json.content)
        self.assertEqual(question_json.json()["results"][0]["correct"], 1)
        self.assertEqual(question_json.json()["results"][1]["unanswered"], 1)
        question_pdf = admin_client.get(question_url + "&export=pdf")
        self.assertEqual(question_pdf.status_code, 200)
        self.assertTrue(question_pdf.content[:4] == bytes([37, 80, 68, 70]))
        override = admin_client.post(
            f"/api/v1/admin/attempts/{attempt_id}/override",
            {"disqualified": True, "reason": "Test disqualification"},
            format="json",
        )
        self.assertEqual(override.status_code, 200)
        self.assertEqual(admin_client.get(class_url).json()["results"], [])
