# Generated for the exam attempt lifecycle.
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0002_immutable_audit"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExamAttempt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attempts", to="portal.exam")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="exam_attempts", to=settings.AUTH_USER_MODEL)),
                ("status", models.CharField(choices=[("IN_PROGRESS", "In progress"), ("SUBMITTED", "Submitted"), ("AUTO_SUBMITTED", "Automatically submitted")], default="IN_PROGRESS", max_length=20)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("deadline_at", models.DateTimeField()),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("last_saved_at", models.DateTimeField(blank=True, null=True)),
                ("session_key", models.UUIDField(default=uuid.uuid4)),
            ],
            options={"db_table": "exam_attempts", "ordering": ["-started_at"]},
        ),
        migrations.AddConstraint(
            model_name="examattempt",
            constraint=models.UniqueConstraint(fields=("exam", "student"), name="unique_exam_attempt_per_student"),
        ),
        migrations.CreateModel(
            name="AttemptAnswer",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="portal.examattempt")),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="portal.question")),
                ("selected_option_id", models.UUIDField(blank=True, null=True)),
                ("saved_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "attempt_answers"},
        ),
        migrations.AddConstraint(
            model_name="attemptanswer",
            constraint=models.UniqueConstraint(fields=("attempt", "question"), name="unique_answer_per_attempt_question"),
        ),
    ]
