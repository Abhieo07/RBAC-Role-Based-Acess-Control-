# Generated by Django 4.0.3 on 2024-11-29 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="otp",
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
