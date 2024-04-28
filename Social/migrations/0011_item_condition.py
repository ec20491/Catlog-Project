# Generated by Django 4.2.6 on 2024-04-11 15:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Social", "0010_item_media_itemimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="condition",
            field=models.CharField(
                choices=[
                    ("NEW", "New"),
                    ("ULN", "Used - Like New"),
                    ("ULG", "Used - Like Good"),
                ],
                default="ULN",
                max_length=3,
            ),
        ),
    ]