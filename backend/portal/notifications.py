from django.utils import timezone

from .models import ScheduledExamNotification


def queue_scheduled_exam_notifications(exam, students):
    """Queue one deduplicated schedule notice for each affected student."""
    revision = f"{exam.start_time.isoformat()}:{exam.end_time.isoformat()}:{exam.duration_minutes}"
    rows = [
        ScheduledExamNotification(
            exam=exam,
            student=student,
            recipient=student.email,
            dedupe_key=f"scheduled:{exam.id}:{student.id}:{revision}",
            due_at=timezone.now(),
        )
        for student in students
        if student.email
    ]
    if rows:
        ScheduledExamNotification.objects.bulk_create(rows, ignore_conflicts=True)
