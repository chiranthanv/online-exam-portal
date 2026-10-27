"""Regression coverage for BL-10: student-facing endpoints never expose answer keys."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import Batch, Exam, ExamBatch, ExamQuestion, Option, Question, StudentBatch, User


class AnswerKeyConfidentialityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="key-admin",
            email="key-admin@example.test",
            name="Key Admin",
            role="ADMIN",
            password="Test-Only-Passphrase-491!",
        )
        cls.student = User.objects.create_user(
            username="key-student",
            email="key-student@example.test",
            name="Key Student",
            usn="KEY-001",
            role="STUDENT",
            password="Test-Only-Passphrase-491!",
        )
        cls.batch = Batch.objects.create(name="KEY-TEST", year=2026)
        StudentBatch.objects.create(student=cls.student, batch=cls.batch)
        cls.question = Question.objects.create(
            text="Which answer is correct?",
            subject="Security",
            topic="Confidentiality",
            difficulty="EASY",
            default_marks="2.00",
            negative_marks="0.50",
            created_by=cls.admin,
        )
        Option.objects.create(question=cls.question, text="Correct answer", is_correct=True)
        Option.objects.create(question=cls.question, text="Distractor", is_correct=False)
        now = timezone.now()
        cls.exam = Exam.objects.create(
            title="Confidentiality test",
            duration_minutes=20,
            start_time=now - timedelta(minutes=1),
            end_time=now + timedelta(minutes=20),
            result_visible_from=now + timedelta(hours=1),
            total_marks="2.00",
            created_by=cls.admin,
        )
        ExamQuestion.objects.create(exam=cls.exam, question=cls.question, sequence=1)
        ExamBatch.objects.create(exam=cls.exam, batch=cls.batch)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    def test_student_cannot_reach_admin_question_or_exam_configuration(self):
        paths = (
            "/api/v1/questions",
            f"/api/v1/questions/{self.question.id}",
            f"/api/v1/exams/{self.exam.id}",
            f"/api/v1/exams/{self.exam.id}/questions",
        )
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403, response.content)
                self.assertNotIn(b"is_correct", response.content)

    def test_available_exam_metadata_contains_no_question_or_answer_key(self):
        response = self.client.get("/api/v1/exams/available")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(response.json()["results"]), 1)
        payload = response.content.decode()
        self.assertNotIn("is_correct", payload)
        self.assertNotIn("Correct answer", payload)
        self.assertNotIn(str(self.question.id), payload)
