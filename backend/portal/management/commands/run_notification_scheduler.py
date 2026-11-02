import time

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Poll the durable notification outboxes on a fixed start-to-start interval."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=float,
            default=60,
            help="Seconds between notification worker starts (default: 60).",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run one notification batch and exit.",
        )

    def handle(self, *args, **options):
        interval = max(1.0, options["interval"])
        while True:
            started = time.monotonic()
            call_command("process_exam_notifications")
            if options["once"]:
                break
            # Keep the cadence start-to-start; do not drift by adding a full
            # interval after a slow delivery batch.
            time.sleep(max(0.0, interval - (time.monotonic() - started)))
