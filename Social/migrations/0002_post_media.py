# Generated by Django 4.2.6 on 2024-02-20 18:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Social", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="media",
            field=models.ImageField(
                blank=True, default="default.png", null=True, upload_to=""
            ),
        ),
    ]
