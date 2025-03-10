# Generated by Django 5.1.4 on 2025-01-19 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charging_station', '0007_alter_chargingsession_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='chargingpoint',
            name='off_peak_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chargingpoint',
            name='off_peak_start',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='chargingsession',
            name='status',
            field=models.CharField(choices=[('Canceled', 'Canceled'), ('Scheduled', 'Scheduled'), ('Confirmed', 'Confirmed'), ('Pending', 'Pending')], default='Scheduled', max_length=100),
        ),
    ]
