from django.db import models
from django.contrib.auth.models import User



# Create your models here.

class Profile(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True, blank=False)
    location = models.CharField(max_length=150, null=True, blank=True)




class ChargingPoint(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    capicity = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    availability = models.BooleanField(null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    off_peak_start = models.TimeField(null=True, blank=True)
    off_peak_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ChargingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    location = models.CharField(max_length=150, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    energy_consumed_kwh = models.FloatField(null=True, blank=True)
    costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=True)
    #created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=[
    ('Canceled', 'Canceled'),
    ('Scheduled', 'Scheduled'),
    ('Confirmed', 'Confirmed'), 
    ('Pending', 'Pending')
    ],
    default='Confirmed'
    )

    def __str__(self):
        return f"Session made by {self.user} at {self.station} - {self.status}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    location = models.CharField(max_length=150)
    start_time = models.DateField()
    end_time = models.DateField(null=True, blank=True)
    costs = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Booking {self.id} made by {self.user} at {self.station}"
    

class PaymentMethods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    card_holder = models.CharField(max_length=50)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"This payment is for {self.user}" 
