"""Queue and deliver exam notifications; schedule this command at least once per minute."""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from portal.models import Attempt, ExamNotification


class Command(BaseCommand):
    help = "Queue due result notices and deliver pending exam notification emails."

    def handle(self, *args, **options):
        now = timezone.now()
        due_attempts = Attempt.objects.filter(
            submitted_at__isnull=False,
            is_disqualified=False,
            exam__result_visible_from__lte=now,
        ).values_list("student_id", "exam_id")
        ExamNotification.objects.bulk_create(
            [
                ExamNotification(student_id=student_id, exam_id=exam_id, notification_type="RESULTS_RELEASED")
                for student_id, exam_id in due_attempts
            ],
            ignore_conflicts=True,
        )

        sent = failed = 0
        pending_ids = list(
            ExamNotification.objects.filter(status__in=["PENDING", "FAILED"], attempts__lt=3)
            .order_by("created_at")
            .values_list("id", flat=True)[:500]
        )
        for notification_id in pending_ids:
            with transaction.atomic():
                notice = (
                    ExamNotification.objects.select_for_update()
                    .select_related("student", "exam")
                    .get(pk=notification_id)
                )
                if notice.status == "SENT" or notice.attempts >= 3:
                    continue
                notice.attempts += 1
                try:
                    if notice.notification_type == "SCHEDULED":
                        subject = f"Exam scheduled: {notice.exam.title}"
                        message = (
                            f"An exam has been scheduled: {notice.exam.title}. "
                            f"Start: {notice.exam.start_time.isoformat()}. "
                            "Sign in to the exam portal for details."
                        )
                    else:
                        subject = f"Results available: {notice.exam.title}"
                        message = (
                            f"Results are now available for {notice.exam.title}. "
                            "Sign in to the exam portal to view your result."
                        )
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [notice.student.email],
                        fail_silently=False,
                    )
                    notice.status = "SENT"
                    notice.sent_at = timezone.now()
                    notice.last_error = ""
                    sent += 1
                except Exception as exc:  # SMTP/provider failures are retried on a later run.
                    notice.status = "FAILED"
                    notice.last_error = type(exc).__name__[:120]
                    failed += 1
                notice.save(update_fields=["attempts", "status", "sent_at", "last_error"])
        self.stdout.write(self.style.SUCCESS(f"Notifications sent={sent} failed={failed}"))
