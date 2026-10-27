import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0003_attempts_and_proctoring"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExamNotification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "notification_type",
                    models.CharField(
                        choices=[("SCHEDULED", "Exam scheduled"), ("RESULTS_RELEASED", "Results released")],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("SENT", "Sent"), ("FAILED", "Failed")],
                        default="PENDING",
                        max_length=10,
                    ),
                ),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("last_error", models.CharField(blank=True, max_length=120)),
                (
                    "exam",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="notifications",
                        to="portal.exam",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="exam_notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "exam_notifications", "ordering": ["created_at", "id"]},
        ),
        migrations.AddConstraint(
            model_name="examnotification",
            constraint=models.UniqueConstraint(
                fields=("student", "exam", "notification_type"), name="one_exam_notification_per_type"
            ),
        ),
    ]
