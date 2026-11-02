from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from portal.models import (
    Batch,
    Exam,
    ExamAttempt,
    ExamBatch,
    NotificationOutbox,
    ScheduledExamNotification,
    StudentBatch,
    User,
)
from portal.notifications import queue_scheduled_exam_notifications


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ScheduledExamNotificationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="schedule-admin",
            email="schedule-admin@example.test",
            name="Admin",
            role="ADMIN",
            password="Test-Password-123!",
        )
        self.students = [
            User.objects.create_user(
                username=f"schedule-student-{i}",
                email=f"schedule-{i}@example.test",
                name=f"Student {i}",
                password="Test-Password-123!",
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

    def test_rescheduling_cancels_obsolete_pending_notice(self):
        ExamBatch.objects.create(exam=self.exam, batch=self.batch)
        queue_scheduled_exam_notifications(self.exam, self.batch.students.all())
        old_notice = ScheduledExamNotification.objects.filter(exam=self.exam).first()
        self.exam.start_time += timedelta(hours=1)
        self.exam.end_time += timedelta(hours=1)
        self.exam.save(update_fields=["start_time", "end_time"])
        queue_scheduled_exam_notifications(self.exam, self.batch.students.all())
        old_notice.refresh_from_db()
        self.assertEqual(old_notice.status, ScheduledExamNotification.CANCELLED)
        self.assertEqual(
            ScheduledExamNotification.objects.filter(
                exam=self.exam, status=ScheduledExamNotification.PENDING
            ).count(),
            len(self.students),
        )

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

    def test_exam_batch_api_queues_schedule_notices_for_assigned_students(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(
            f"/api/v1/exams/{self.exam.id}/batches",
            {"batch_ids": [str(self.batch.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            ScheduledExamNotification.objects.filter(exam=self.exam).count(),
            len(self.students),
        )

    def test_result_email_waits_for_release_and_is_sent_once(self):
        now = timezone.now()
        self.exam.result_visible_from = now - timedelta(minutes=1)
        self.exam.save(update_fields=["result_visible_from"])
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            student=self.students[0],
            status=ExamAttempt.SUBMITTED,
            deadline_at=now,
            submitted_at=now,
            evaluated_at=now,
            score="10.00",
        )
        NotificationOutbox.objects.create(
            attempt=attempt,
            recipient=self.students[0].email,
            dedupe_key=f"result:{attempt.id}",
            due_at=now,
        )
        call_command("process_exam_notifications")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Results available", mail.outbox[0].subject)
        call_command("process_exam_notifications")
        self.assertEqual(len(mail.outbox), 1)

    def test_result_email_is_not_sent_before_the_release_time(self):
        now = timezone.now()
        self.exam.result_visible_from = now + timedelta(hours=1)
        self.exam.save(update_fields=["result_visible_from"])
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            student=self.students[0],
            status=ExamAttempt.SUBMITTED,
            deadline_at=now,
            submitted_at=now,
            evaluated_at=now,
            score="10.00",
        )
        notice = NotificationOutbox.objects.create(
            attempt=attempt,
            recipient=self.students[0].email,
            dedupe_key=f"result:{attempt.id}",
            due_at=now,
        )
        call_command("process_exam_notifications")
        notice.refresh_from_db()
        self.assertEqual(mail.outbox, [])
        self.assertEqual(notice.due_at, self.exam.result_visible_from)

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


    def test_notification_scheduler_runs_one_batch_in_once_mode(self):
        from unittest.mock import patch

        with patch("portal.management.commands.run_notification_scheduler.call_command") as run_batch:
            call_command("run_notification_scheduler", once=True, interval=60)
        run_batch.assert_called_once_with("process_exam_notifications")
