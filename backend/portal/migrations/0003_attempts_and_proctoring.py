import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0002_immutable_audit"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attempt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("score", models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ("is_disqualified", models.BooleanField(default=False)),
                ("disqualification_reason", models.CharField(blank=True, max_length=500)),
                ("overridden_at", models.DateTimeField(blank=True, null=True)),
                (
                    "exam",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attempts", to="portal.exam"),
                ),
                (
                    "overridden_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="attempt_overrides",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="exam_attempts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "exam_attempts", "ordering": ["-started_at", "id"]},
        ),
        migrations.AddConstraint(
            model_name="attempt",
            constraint=models.UniqueConstraint(fields=("student", "exam"), name="one_attempt_per_student_exam"),
        ),
        migrations.CreateModel(
            name="AttemptAnswer",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("awarded_marks", models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                (
                    "attempt",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="portal.attempt"),
                ),
                (
                    "question",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="portal.question"),
                ),
                (
                    "selected_option",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="portal.option",
                    ),
                ),
            ],
            options={"db_table": "attempt_answers"},
        ),
        migrations.AddConstraint(
            model_name="attemptanswer",
            constraint=models.UniqueConstraint(
                fields=("attempt", "question"), name="one_answer_per_attempt_question"
            ),
        ),
        migrations.CreateModel(
            name="ProctoringFlag",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "event_type",
                    models.CharField(
                        choices=[("TAB_SWITCH", "Tab switch"), ("WINDOW_BLUR", "Window blur")], max_length=20
                    ),
                ),
                ("occurred_at", models.DateTimeField()),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attempt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="proctoring_flags",
                        to="portal.attempt",
                    ),
                ),
            ],
            options={"db_table": "proctoring_flags", "ordering": ["received_at", "id"]},
        ),
    ]
