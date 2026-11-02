import time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from portal.assessment import evaluate_attempt
from portal.models import AuditLog, ExamAttempt, NotificationOutbox


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
                    ExamAttempt.objects.select_for_update(of=("self",))
                    .select_related("student", "exam")
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
                    evaluate_attempt(attempt, now=now)
                    NotificationOutbox.objects.get_or_create(
                        dedupe_key="result:" + str(attempt.id),
                        defaults={
                            "attempt": attempt,
                            "recipient": attempt.student.email,
                            "due_at": attempt.exam.result_visible_from,
                        },
                    )
                    AuditLog.objects.create(
                        actor=attempt.student, action="EXAM_ATTEMPT_AUTO_SUBMITTED", target=str(attempt.id)
                    )
            if expired:
                self.stdout.write(self.style.SUCCESS(f"Auto-submitted {len(expired)} expired attempt(s)."))
            if not options["loop"]:
                break
            time.sleep(interval)
