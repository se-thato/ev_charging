# Generated by Django 5.1.4 on 2025-02-28 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charging_station", "0021_alter_chargingsession_location"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chargingsession",
            name="location",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
