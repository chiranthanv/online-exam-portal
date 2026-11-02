from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from portal.models import NotificationOutbox


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
                    NotificationOutbox.objects.select_for_update()
                    .select_related("attempt__exam", "attempt__student")
                    .get(pk=candidate.pk)
                )
                if item.status == NotificationOutbox.SENT or item.due_at > timezone.now():
                    continue
                item.attempts += 1
                try:
                    if item.attempt.disqualification_reason:
                        item.status = NotificationOutbox.SENT
                        item.sent_at = timezone.now()
                        item.last_error = "Suppressed: attempt is disqualified."
                        item.save(update_fields=["attempts", "status", "sent_at", "last_error"])
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
                    item.last_error = str(exc)[:500]
                    failed += 1
                item.save(update_fields=["attempts", "status", "sent_at", "last_error"])
        self.stdout.write(self.style.SUCCESS(f"Delivered {delivered}; failed {failed}."))
