from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0007_attempt_disqualification_restore_state")]

    operations = [
        migrations.AlterField(
            model_name="examattempt",
            name="score",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
