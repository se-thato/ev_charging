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

    def __str__(self):
        return self.name

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=100, choices=[('Reserved', 'Reserved'), ('Completed', 'Completed')])

    def __str__(self):
        return f"{self.user.username} - {self.station.name} - {self.status}"