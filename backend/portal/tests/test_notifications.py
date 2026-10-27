"""Regression tests for de-duplicated exam email notifications."""

from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import (
    Attempt,
    Batch,
    Exam,
    ExamNotification,
    StudentBatch,
    User,
)


class ExamNotificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="notice-admin",
            email="notice-admin@example.test",
            name="Notice Admin",
            role="ADMIN",
            password="Test-Only-Passphrase-491!",
        )
        cls.student = User.objects.create_user(
            username="notice-student",
            email="notice-student@example.test",
            name="Notice Student",
            usn="NOTICE-001",
            role="STUDENT",
            password="Test-Only-Passphrase-491!",
        )
        cls.batch = Batch.objects.create(name="NOTICE-TEST", year=2026)
        StudentBatch.objects.create(student=cls.student, batch=cls.batch)
        now = timezone.now()
        cls.exam = Exam.objects.create(
            title="Notification exam",
            duration_minutes=30,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=3),
            result_visible_from=now + timedelta(hours=4),
            total_marks="2.00",
            created_by=cls.admin,
        )

    def test_assignment_queues_one_schedule_notice_per_student(self):
        client = APIClient()
        client.force_authenticate(user=self.admin)
        url = f"/api/v1/exams/{self.exam.id}/batches"
        payload = {"batch_ids": [str(self.batch.id)]}
        first = client.post(url, payload, format="json")
        second = client.post(url, payload, format="json")
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(
            ExamNotification.objects.filter(
                student=self.student, exam=self.exam, notification_type="SCHEDULED"
            ).count(),
            1,
        )

    @patch("portal.management.commands.process_exam_notifications.send_mail")
    def test_due_result_notice_is_queued_and_success_is_not_resent(self, send_mail_mock):
        self.exam.result_visible_from = timezone.now() - timedelta(seconds=1)
        self.exam.save(update_fields=["result_visible_from"])
        attempt = Attempt.objects.create(
            student=self.student,
            exam=self.exam,
            submitted_at=timezone.now() - timedelta(minutes=1),
            score="2.00",
        )
        call_command("process_exam_notifications")
        notice = ExamNotification.objects.get(
            student=self.student, exam=self.exam, notification_type="RESULTS_RELEASED"
        )
        self.assertEqual(notice.status, "SENT")
        self.assertEqual(notice.attempts, 1)
        self.assertEqual(send_mail_mock.call_count, 1)
        self.assertEqual(send_mail_mock.call_args.args[3], [self.student.email])
        call_command("process_exam_notifications")
        self.assertEqual(send_mail_mock.call_count, 1)
        self.assertEqual(Attempt.objects.get(pk=attempt.pk).score, 2)

    @patch(
        "portal.management.commands.process_exam_notifications.send_mail",
        side_effect=[RuntimeError("provider secret must not be persisted"), None],
    )
    def test_failed_delivery_is_retried_without_storing_provider_message(self, send_mail_mock):
        ExamNotification.objects.create(
            student=self.student, exam=self.exam, notification_type="SCHEDULED"
        )
        call_command("process_exam_notifications")
        notice = ExamNotification.objects.get(notification_type="SCHEDULED")
        self.assertEqual(notice.status, "FAILED")
        self.assertEqual(notice.last_error, "RuntimeError")
        self.assertNotIn("provider secret", notice.last_error)
        call_command("process_exam_notifications")
        notice.refresh_from_db()
        self.assertEqual(notice.status, "SENT")
        self.assertEqual(notice.attempts, 2)
        self.assertEqual(send_mail_mock.call_count, 2)
