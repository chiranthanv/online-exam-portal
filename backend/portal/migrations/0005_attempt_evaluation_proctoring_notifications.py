# Generated for current ExamAttempt lifecycle integration.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0004_alter_examattempt_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name="examattempt", name="score", field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
        migrations.AddField(model_name="examattempt", name="evaluated_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="examattempt", name="disqualification_reason", field=models.CharField(blank=True, default="", max_length=500)),
        migrations.AddField(model_name="examattempt", name="overridden_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="examattempt", name="overridden_by", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="attempt_overrides", to=settings.AUTH_USER_MODEL)),
        migrations.CreateModel(
            name="ProctoringEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_type", models.CharField(choices=[("TAB_SWITCH", "Tab switch"), ("WINDOW_BLUR", "Window blur")], max_length=20)),
                ("occurred_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proctoring_events", to="portal.examattempt")),
            ],
            options={"db_table": "proctoring_events", "ordering": ["occurred_at", "id"]},
        ),
        migrations.CreateModel(
            name="NotificationOutbox",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("recipient", models.EmailField(max_length=150)),
                ("kind", models.CharField(default="RESULT_AVAILABLE", max_length=40)),
                ("dedupe_key", models.CharField(max_length=200, unique=True)),
                ("due_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("SENT", "Sent"), ("FAILED", "Failed")], default="PENDING", max_length=10)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("last_error", models.CharField(blank=True, default="", max_length=500)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="portal.examattempt")),
            ],
            options={"db_table": "notification_outbox", "ordering": ["due_at", "id"]},
        ),
    ]
