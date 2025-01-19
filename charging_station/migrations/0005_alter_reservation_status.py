# Generated by Django 5.1.4 on 2025-01-18 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charging_station', '0004_chargingsession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('Canceled', 'Canceled'), ('Confirmed', 'Confirmed'), ('Pending', 'Pending')], max_length=100),
        ),
    ]
