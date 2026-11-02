from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0006_scheduled_exam_notifications")]
    operations = [
        migrations.AddField(
            model_name="examattempt",
            name="status_before_disqualification",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
