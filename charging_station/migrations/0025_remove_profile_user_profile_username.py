# Generated by Django 5.1.7 on 2025-04-05 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charging_station', '0024_remove_chargingsession_location_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.AddField(
            model_name='profile',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
