from django.utils import timezone

from .models import ScheduledExamNotification


def queue_scheduled_exam_notifications(exam, students):
    """Queue one deduplicated schedule notice for each affected student."""
    revision = f"{exam.start_time.isoformat()}:{exam.end_time.isoformat()}:{exam.duration_minutes}"
    students = list(students)
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
    current_keys = [row.dedupe_key for row in rows]
    if students:
        ScheduledExamNotification.objects.filter(
            exam=exam,
            student__in=students,
            status__in=[ScheduledExamNotification.PENDING, ScheduledExamNotification.FAILED],
        ).exclude(dedupe_key__in=current_keys).update(
            status=ScheduledExamNotification.CANCELLED,
            last_error="Superseded by a newer exam schedule.",
        )
    if rows:
        ScheduledExamNotification.objects.bulk_create(rows, ignore_conflicts=True)
