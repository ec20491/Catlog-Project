# Generated by Django 4.2.6 on 2024-04-04 23:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Users", "0006_veterinaryprofessional"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="veterinaryprofessional",
            name="verified",
        ),
    ]
