# Generated by Django 4.0.3 on 2024-11-30 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0004_alter_user_is_active"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_active",
        ),
    ]
