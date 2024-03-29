# Generated by Django 3.1.2 on 2020-11-13 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20201113_1041'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_verified',
            new_name='is_email_verified',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_phone_verified',
            field=models.BooleanField(default=False),
        ),
    ]
