# Generated by Django 5.1.6 on 2025-04-24 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('follow', '0002_followrequest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending', max_length=10),
        ),
    ]
