# Generated by Django 5.1.1 on 2024-10-13 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_module', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_activate',
            field=models.BooleanField(default=False),
        ),
    ]