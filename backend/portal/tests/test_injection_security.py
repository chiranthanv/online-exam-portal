"""Regression tests for issue BL-20: injection inputs stay data, not queries or code."""

from django.test import TestCase
from rest_framework.test import APIClient

from portal.models import Option, Question, User


class InjectionRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="security-admin",
            email="security-admin@example.test",
            name="Security Admin",
            role="ADMIN",
            password="Test-Only-Passphrase-491!",
        )
        cls.question = Question.objects.create(
            text="Initial question",
            subject="SE",
            topic="Security",
            difficulty="EASY",
            default_marks="2.00",
            negative_marks="0.00",
            created_by=cls.admin,
        )
        Option.objects.create(question=cls.question, text="Correct", is_correct=True)
        Option.objects.create(question=cls.question, text="Incorrect", is_correct=False)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_sql_injection_filter_is_treated_as_a_literal_value(self):
        response = self.client.get("/api/v1/questions?subject=%27%20OR%201%3D1%20--")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["count"], 0)
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())

    def test_script_payload_remains_text_when_question_is_edited(self):
        payload = "<script>alert('xss')</script>'; DROP TABLE users; --"
        response = self.client.patch(
            f"/api/v1/questions/{self.question.pk}",
            {"text": payload},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["text"], payload)

        self.question.refresh_from_db()
        self.assertEqual(self.question.text, payload)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Option.objects.filter(question=self.question).count(), 2)
