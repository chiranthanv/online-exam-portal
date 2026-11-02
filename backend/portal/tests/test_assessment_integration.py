from datetime import timedelta

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


class AttemptAssessmentIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="faculty-assessment",
            email="faculty-assessment@example.test",
            name="Faculty",
            role="ADMIN",
            password="Assessment-Test-Password-123!"
        )
        cls.student = User.objects.create_user(
            username="student-assessment",
            email="student-assessment@example.test",
            name="Student",
            usn="ASSESS-001",
            password="Assessment-Test-Password-123!"
        )
        cls.question = Question.objects.create(
            text="2 + 2?",
            subject="Math",
            topic="Arithmetic",
            difficulty="EASY",
            default_marks="2.00",
            negative_marks="0.50",
            created_by=cls.admin,
        )
        cls.correct = Option.objects.create(question=cls.question, text="4", is_correct=True)
        cls.wrong = Option.objects.create(question=cls.question, text="5", is_correct=False)
        now = timezone.now()
        cls.exam = Exam.objects.create(
            title="Assessment integration",
            duration_minutes=30,
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            result_visible_from=now - timedelta(minutes=1),
            total_marks="2.00",
            created_by=cls.admin,
        )
        ExamQuestion.objects.create(exam=cls.exam, question=cls.question, sequence=1)

    def make_attempt(self, status=ExamAttempt.IN_PROGRESS, option=None):
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            student=self.student,
            status=status,
            deadline_at=timezone.now() + timedelta(minutes=10),
        )
        if option is not None:
            AttemptAnswer.objects.create(
                attempt=attempt, question=self.question, selected_option_id=option.id
            )
        return attempt

    def test_submission_scores_saved_answers_but_hides_score_until_release(self):
        attempt = self.make_attempt(option=self.correct)
        client = APIClient()
        client.force_authenticate(self.student)
        response = client.post(
            f"/api/v1/attempts/{attempt.id}/submit",
            {},
            format="json",
            HTTP_X_EXAM_SESSION=str(attempt.session_key),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotIn("score", response.data)
        attempt.refresh_from_db()
        self.assertEqual(str(attempt.score), "2.00")
        self.assertIsNotNone(attempt.evaluated_at)
        result = client.get(
            f"/api/v1/attempts/{attempt.id}/result",
            HTTP_X_EXAM_SESSION=str(attempt.session_key),
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["score"], "2.00")

    def test_negative_score_is_clamped_to_zero(self):
        attempt = self.make_attempt(option=self.wrong)
        client = APIClient()
        client.force_authenticate(self.student)
        response = client.post(
            f"/api/v1/attempts/{attempt.id}/submit", {}, format="json",
            HTTP_X_EXAM_SESSION=str(attempt.session_key),
        )
        self.assertEqual(response.status_code, 200, response.content)
        attempt.refresh_from_db()
        self.assertEqual(str(attempt.score), "0.00")
    def test_result_is_hidden_before_release(self):
        self.exam.result_visible_from = timezone.now() + timedelta(hours=1)
        self.exam.save(update_fields=["result_visible_from"])
        attempt = self.make_attempt(status=ExamAttempt.SUBMITTED, option=self.correct)
        attempt.submitted_at = timezone.now()
        attempt.score = "2.00"
        attempt.evaluated_at = timezone.now()
        attempt.save(update_fields=["submitted_at", "score", "evaluated_at"])
        client = APIClient()
        client.force_authenticate(self.student)
        response = client.get(f"/api/v1/attempts/{attempt.id}/result")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("score", response.data)

    def test_student_proctoring_event_requires_attempt_session(self):
        attempt = self.make_attempt()
        client = APIClient()
        client.force_authenticate(self.student)
        url = f"/api/v1/attempts/{attempt.id}/proctoring-events"
        bad = client.post(url, {"event_type": "TAB_SWITCH"}, format="json")
        self.assertEqual(bad.status_code, 409)
        good = client.post(
            url,
            {"event_type": "TAB_SWITCH"},
            format="json",
            HTTP_X_EXAM_SESSION=str(attempt.session_key),
        )
        self.assertEqual(good.status_code, 201)
        self.assertEqual(ProctoringEvent.objects.filter(attempt=attempt).count(), 1)

    def test_admin_can_disqualify_and_repermit_terminal_attempt(self):
        attempt = self.make_attempt(status=ExamAttempt.SUBMITTED)
        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["submitted_at"])
        client = APIClient()
        client.force_authenticate(self.admin)
        url = f"/api/v1/admin/attempts/{attempt.id}/override"
        denied = client.post(url, {"disqualified": True, "reason": ""}, format="json")
        self.assertEqual(denied.status_code, 400)
        changed = client.post(url, {"disqualified": True, "reason": "Reviewed flag evidence"}, format="json")
        self.assertEqual(changed.status_code, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.DISQUALIFIED)
        restored = client.post(url, {"disqualified": False, "reason": ""}, format="json")
        self.assertEqual(restored.status_code, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.SUBMITTED)
        self.assertEqual(AuditLog.objects.filter(target=str(attempt.id)).count(), 2)
