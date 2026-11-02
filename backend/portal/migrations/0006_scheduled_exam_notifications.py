from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0005_attempt_evaluation_proctoring_notifications"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="ScheduledExamNotification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("recipient", models.EmailField(max_length=150)),
                ("dedupe_key", models.CharField(max_length=200, unique=True)),
                ("due_at", models.DateTimeField()),
                ("status", models.CharField(choices=[
                    ("PENDING", "Pending"), ("SENT", "Sent"),
                    ("FAILED", "Failed"), ("CANCELLED", "Cancelled")
                ], default="PENDING", max_length=10)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("last_error", models.CharField(blank=True, default="", max_length=500)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name="scheduled_notifications", to="portal.exam")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name="scheduled_exam_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "scheduled_exam_notifications", "ordering": ["due_at", "id"]},
        ),
    ]
