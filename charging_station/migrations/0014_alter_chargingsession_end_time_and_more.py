# Generated by Django 5.1.4 on 2025-02-01 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charging_station', '0013_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chargingsession',
            name='end_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='chargingsession',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
