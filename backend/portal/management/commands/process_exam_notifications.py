from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from portal.models import ExamBatch, NotificationOutbox, ScheduledExamNotification


class Command(BaseCommand):
    help = "Deliver due exam-result notifications from the transactional outbox."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        delivered = 0
        failed = 0
        now = timezone.now()
        candidates = NotificationOutbox.objects.filter(
            status__in=[NotificationOutbox.PENDING, NotificationOutbox.FAILED],
            due_at__lte=now,
            attempts__lt=5,
        ).order_by("due_at")[: max(1, min(options["limit"], 500))]
        for candidate in candidates:
            with transaction.atomic():
                item = (
                    NotificationOutbox.objects.select_for_update(of=("self",))
                    .select_related("attempt__exam", "attempt__student")
                    .get(pk=candidate.pk)
                )
                if item.status == NotificationOutbox.SENT or item.due_at > timezone.now():
                    continue
                item.attempts += 1
                try:
                    if item.attempt.evaluated_at is None:
                        item.due_at = timezone.now() + timedelta(minutes=1)
                        item.last_error = "Waiting for server-side evaluation."
                        item.save(update_fields=["due_at", "last_error"])
                        continue
                    if timezone.now() < item.attempt.exam.result_visible_from:
                        item.due_at = item.attempt.exam.result_visible_from
                        item.save(update_fields=["due_at"])
                        continue
                    if item.attempt.status == "DISQUALIFIED" or item.attempt.disqualification_reason:
                        item.status = NotificationOutbox.SENT
                        item.sent_at = timezone.now()
                        item.last_error = "Suppressed: attempt is disqualified."
                        item.save(update_fields=["attempts", "status", "sent_at", "last_error", "due_at"])
                        continue
                    send_mail(
                        subject=f"Results available: {item.attempt.exam.title}",
                        message=(
                            f"Your result for {item.attempt.exam.title} is now available. "
                            "Sign in to the exam portal to view your result."
                        ),
                        from_email=None,
                        recipient_list=[item.recipient],
                        fail_silently=False,
                    )
                    item.status = NotificationOutbox.SENT
                    item.sent_at = timezone.now()
                    item.last_error = ""
                    delivered += 1
                except Exception as exc:
                    item.status = NotificationOutbox.FAILED
                    item.last_error = type(exc).__name__[:120]
                    item.due_at = timezone.now() + timedelta(minutes=min(2**item.attempts, 60))
                    failed += 1
                item.save(update_fields=["attempts", "status", "sent_at", "last_error", "due_at"])

        schedule_candidates = ScheduledExamNotification.objects.filter(
            status__in=[ScheduledExamNotification.PENDING, ScheduledExamNotification.FAILED],
            due_at__lte=timezone.now(),
            attempts__lt=5,
        ).order_by("due_at", "created_at")[: max(1, min(options["limit"], 500))]
        for candidate in schedule_candidates:
            with transaction.atomic():
                item = (
                    ScheduledExamNotification.objects.select_for_update()
                    .select_related("exam", "student")
                    .get(pk=candidate.pk)
                )
                if item.status in {ScheduledExamNotification.SENT, ScheduledExamNotification.CANCELLED}:
                    continue
                if item.due_at > timezone.now() or item.attempts >= 5:
                    continue
                if not ExamBatch.objects.filter(exam=item.exam, batch__students=item.student).exists():
                    item.status = ScheduledExamNotification.CANCELLED
                    item.last_error = "Suppressed: student is no longer assigned to this exam."
                    item.save(update_fields=["status", "last_error"])
                    continue
                item.attempts += 1
                try:
                    send_mail(
                        subject=f"Exam scheduled: {item.exam.title}",
                        message=(
                            f"An exam has been scheduled: {item.exam.title}.\n"
                            f"Start: {item.exam.start_time.isoformat()}\n"
                            f"End: {item.exam.end_time.isoformat()}\n"
                            f"Duration: {item.exam.duration_minutes} minutes.\n"
                            "Sign in to the exam portal for details."
                        ),
                        from_email=None,
                        recipient_list=[item.recipient],
                        fail_silently=False,
                    )
                    item.status = ScheduledExamNotification.SENT
                    item.sent_at = timezone.now()
                    item.last_error = ""
                except Exception as exc:
                    item.status = ScheduledExamNotification.FAILED
                    item.last_error = type(exc).__name__[:120]
                    item.due_at = timezone.now() + timedelta(minutes=min(2**item.attempts, 60))
                item.save(update_fields=["attempts", "status", "sent_at", "last_error", "due_at"])
        self.stdout.write(self.style.SUCCESS(f"Delivered {delivered}; failed {failed}."))
