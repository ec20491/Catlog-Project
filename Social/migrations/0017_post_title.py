# Generated by Django 4.2.6 on 2024-04-27 23:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Social", "0016_alter_item_longitude"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="title",
            field=models.TextField(default="This is the title"),
        ),
    ]