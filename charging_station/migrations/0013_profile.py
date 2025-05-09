# Generated by Django 5.1.4 on 2025-01-27 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charging_station", "0012_alter_chargingpoint_availability"),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=50)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=100, unique=True)),
            ],
        ),
    ]
