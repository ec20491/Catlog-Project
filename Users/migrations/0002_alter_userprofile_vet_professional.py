# Generated by Django 4.2.6 on 2024-02-19 22:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="vet_professional",
            field=models.BooleanField(null=True),
        ),
    ]
