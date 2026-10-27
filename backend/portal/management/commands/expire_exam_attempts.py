import time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from portal.models import AuditLog, ExamAttempt


class Command(BaseCommand):
    help = "Automatically submit expired exam attempts (run once or as a polling worker)."

    def add_arguments(self, parser):
        parser.add_argument("--loop", action="store_true", help="Poll continuously until stopped.")
        parser.add_argument("--interval", type=float, default=5, help="Polling interval in seconds.")

    def handle(self, *args, **options):
        interval = max(1.0, options["interval"])
        while True:
            with transaction.atomic():
                expired = list(
                    ExamAttempt.objects.select_for_update()
                    .select_related("student")
                    .filter(status=ExamAttempt.IN_PROGRESS, deadline_at__lte=timezone.now())
                    .order_by("deadline_at")
                )
                now = timezone.now()
                for attempt in expired:
                    # The row lock and status recheck make concurrent workers safe.
                    if attempt.status != ExamAttempt.IN_PROGRESS or attempt.deadline_at > now:
                        continue
                    attempt.status = ExamAttempt.AUTO_SUBMITTED
                    attempt.submitted_at = now
                    attempt.save(update_fields=["status", "submitted_at"])
                    AuditLog.objects.create(
                        actor=attempt.student,
                        action="EXAM_ATTEMPT_AUTO_SUBMITTED",
                        target=str(attempt.id),
                    )
            if expired:
                self.stdout.write(self.style.SUCCESS(f"Auto-submitted {len(expired)} expired attempt(s)."))
            if not options["loop"]:
                break
            time.sleep(interval)
