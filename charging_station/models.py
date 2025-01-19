from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChargingPoint(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    capicity = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    availability = models.BooleanField(default=True)
    off_peak_start = models.TimeField(null=True, blank=True)
    off_peak_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ChargingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    energy_consumed_kwh = models.FloatField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=100, choices=[
    ('Canceled', 'Canceled'),
    ('Scheduled', 'Scheduled'),
    ('Confirmed', 'Confirmed'), 
    ('Pending', 'Pending')
    ],
    default='Scheduled'
    )

    def __str__(self):
        return f"Session made by {self.user} at {self.station} - {self.status}"