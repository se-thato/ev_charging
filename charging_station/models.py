from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError  
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()



# Create your models here.

class Profile(models.Model):
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True, blank=False)
    location = models.CharField(max_length=150, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.username



class ChargingPoint(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, null=True, blank=True)
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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='charging_points_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='charging_points_updated')


    def __str__(self):
        return self.name



class ChargingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    energy_consumed_kwh = models.FloatField(null=True, blank=True)
    costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.0)
    #created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=[
    ('Canceled', 'Canceled'),
    ('Scheduled', 'Scheduled'),
    ('Confirmed', 'Confirmed'), 
    ('Pending', 'Pending')
    ],
    default='Confirmed'
    )
    duration = models.DurationField(null=True, blank=True)

    #this method calculates the duration of the session
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            if self.end_time < self.start_time:
                raise ValidationError("Opps!! end time cannot be before start time.")
            self.duration = self.end_time - self.start_time   
        super().save(*args, **kwargs) 


    def __str__(self):
        return f"Session made by {self.user} at {self.station} - {self.status}"



class Booking(models.Model):
    class Meta:
        unique_together = ('user', 'station', 'start_time', 'end_time')

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
    payment = models.ForeignKey('PaymentMethod', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bookings_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bookings_updated')

    def __str__(self):
        return f"Booking {self.id} made by {self.user} at {self.station}"
    


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # This will notify the user when a booking is created
    @receiver(post_save, sender=Booking)
    def create_notification(sender, instance, created, **kwargs):
        if created:
            Notification.objects.create(
                user=instance.user,
                message=f"Booking confirmed for {instance.station} from {instance.start_time} to {instance.end_time}."
            )


    def __str__(self):
        return f"Notification for {self.user} - {'Seen' if self.is_read else 'Unseen'}"



class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=15, choices=PAYMENT_TYPES)
    last_four_digits = models.CharField(max_length=4, blank=True) #this is for credit/debit cards last four digits
    expiration_date = models.DateField(null=True, blank=True) #this is for credit/debit cards
    email = models.EmailField(max_length=100, blank=True)  #this is for PayPal or bank transfer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)  #this is to set a default payment method

    #to prevent repetitive payment methods
    class Meta:
        unique_together = ('user', 'payment_type', 'last_four_digits', 'email')
        ordering = ['-created_at'] # Order by most recent first


    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.user.username}"



class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    currency = models.CharField(max_length=3)
    charging_session = models.ForeignKey(ChargingSession, on_delete=models.SET_NULL, null=True, blank=True)
    

    #gateway metadata
    gateway_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)  # Store the response from the payment gateway as JSON

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [ 
            models.Index(fields=['gateway_transaction_id']), #this will help in searching for a transaction
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"payment {self.id} - {self.currency}{self.amount} ({self.get_status_display()})"



class Rating(models.Model):
    class Meta:
        #this will prevent a user from rating the same station multiple times
        unique_together = ('user', 'station')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ratings_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ratings_updated')

    def save(self, *args, **kwargs):
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rating by {self.user} for {self.station} - {self.rating}"



class IssueReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Issue reported by {self.user} for {self.station} - {'Resolved' if self.resolved else 'Unresolved'}"



class Comment(models.Model):
    class Meta:
        unique_together = ('user', 'station')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"Comment made by {self.user} for {self.station}"

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes

    #this will prevent a user from commenting the same station multiple times
    def save(self, *args, **kwargs):
        if Comment.objects.filter(user=self.user, station=self.station, comment_text=self.comment_text).exists():
            raise ValidationError("Duplicate comment is not allowed.")
        super().save(*args, **kwargs)
    

#managing subscription plans for users
#this will help in managing the subscription plans for users
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_days = models.DurationField()
    features = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} - {self.price} for {self.duration_in_days} days"
    

#now tracking which users are subscribed to which plan
class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.user} subscribed to {self.plan.name} until {self.end_date}"



class ChargingStationAnalitics(models.Model):
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    total_sessions = models.PositiveIntegerField(default=0)
    total_energy_consumed = models.FloatField(default=0.0)  # in kWh
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # in currency
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics for {self.station} - {self.total_sessions} sessions"



