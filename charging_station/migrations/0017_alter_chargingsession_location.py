# Generated by Django 5.1.4 on 2025-02-28 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charging_station", "0016_booking_payment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chargingsession",
            name="location",
            field=models.CharField(max_length=150),
        ),
    ]
