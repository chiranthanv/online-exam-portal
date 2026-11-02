from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from portal.models import Batch, Exam, ExamBatch, ScheduledExamNotification, StudentBatch, User
from portal.notifications import queue_scheduled_exam_notifications


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ScheduledExamNotificationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="schedule-admin", email="schedule-admin@example.test",
            name="Admin", role="ADMIN", password="Test-Password-123!",
        )
        self.students = [
            User.objects.create_user(
                username=f"schedule-student-{i}", email=f"schedule-{i}@example.test",
                name=f"Student {i}", password="Test-Password-123!",
            )
            for i in range(2)
        ]
        self.batch = Batch.objects.create(name="SCHEDULE-CSE", year=2026)
        for student in self.students:
            StudentBatch.objects.create(student=student, batch=self.batch)
        now = timezone.now()
        self.exam = Exam.objects.create(
            title="Scheduled exam",
            duration_minutes=30,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=3),
            result_visible_from=now + timedelta(hours=4),
            total_marks="10.00",
            created_by=self.admin,
        )

    def test_assignment_queue_deduplicates_per_student(self):
        ExamBatch.objects.create(exam=self.exam, batch=self.batch)
        queue_scheduled_exam_notifications(self.exam, self.batch.students.all())
        queue_scheduled_exam_notifications(self.exam, self.batch.students.all())
        self.assertEqual(ScheduledExamNotification.objects.filter(exam=self.exam).count(), 2)

    def test_worker_sends_each_schedule_notice_once(self):
        ExamBatch.objects.create(exam=self.exam, batch=self.batch)
        queue_scheduled_exam_notifications(self.exam, self.batch.students.all())
        call_command("process_exam_notifications")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            ScheduledExamNotification.objects.filter(status=ScheduledExamNotification.SENT).count(), 2
        )
        call_command("process_exam_notifications")
        self.assertEqual(len(mail.outbox), 2)

    def test_retry_does_not_persist_smtp_error_details(self):
        ExamBatch.objects.create(exam=self.exam, batch=self.batch)
        queue_scheduled_exam_notifications(self.exam, [self.students[0]])
        with patch(
            "portal.management.commands.process_exam_notifications.send_mail",
            side_effect=RuntimeError("smtp password=private"),
        ):
            call_command("process_exam_notifications")
        notice = ScheduledExamNotification.objects.get()
        self.assertEqual(notice.status, ScheduledExamNotification.FAILED)
        self.assertEqual(notice.attempts, 1)
        self.assertNotIn("password", notice.last_error.lower())
        self.assertGreater(notice.due_at, timezone.now())
