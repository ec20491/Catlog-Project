# Generated by Django 4.2.6 on 2024-04-22 12:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Users", "0010_veterinaryprofessional_verification_code_expires"),
    ]

    operations = [
        migrations.AddField(
            model_name="veterinaryprofessional",
            name="verification_code",
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
