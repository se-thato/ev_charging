from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django.conf import settings



User = get_user_model()


class Profile(models.Model):
    username = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    #Ev specific fields
    vehicle_make = models.CharField(max_length=50, null=True, blank=True)
    vehicle_model = models.CharField(max_length=50, null=True, blank=True)
    vehicle_year = models.PositiveIntegerField(null=True, blank=True)
    connector_type = models.CharField(max_length=50, null=True, blank=True,
                                      choices= [
                                          ('ccs2', 'CCS2'),
                                          ('chademo', 'CHAdeMO'),
                                          ('type1', 'Type 1'),
                                          ('type2', 'Type 2'),
                                          ('tesla', 'Tesla'),
                                          ('other', 'Other'),
                                      ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username




class StationOwnerProfile(models.Model): 
    """
    Profile for station owners.
    Created manually when a user registers as an owner.
    A user can have both a UserProfile and a StationOwnerProfile
    """

    """
    this verification status will help us manage the onboarding process of station owners
    and ensure we have all the necessary information before they can start listing stations and receiving payouts.
    It also allows us to track where each owner is in the verification process and
    take appropriate actions (send reminders, flag for review.) based on their status.
    """
    VERIFICATION_STATUS = [
        ('unverified', 'Unverified'),
        ('pending',    'Pending review'),
        ('verified',   'Verified'),
        ('suspended',  'Suspended'),
    ]

    LISTING_TIER = [
        ('free',     'Free'),
        ('featured', 'Featured'),
        ('premium',  'Premium'),
    ]

    PAYOUT_SCHEDULE = [
        ('weekly',   'Weekly (every Monday)'),
        ('biweekly', 'Bi-weekly'),
        ('monthly',  'Monthly'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='owner_profile')
    # Business identity
    business_name = models.CharField(max_length=150)
    business_reg_number = models.CharField(max_length=50, null=True, blank=True)
    vat_number = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    logo = models.ImageField(upload_to='owner_logos/', null=True, blank=True)
    id_document = models.FileField(upload_to='owner_docs/', null=True, blank=True)

    # Verification
    verification_status = models.CharField(max_length=20,choices=VERIFICATION_STATUS,default='unverified')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True, blank=True,related_name='owners_verified')

    # SA banking details account_number will be encrypted
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_holder = models.CharField(max_length=150, null=True, blank=True)
    account_number = models.CharField(max_length=30, null=True, blank=True)  # will encrypt
    branch_code = models.CharField(max_length=10, null=True, blank=True)
    account_type = models.CharField(max_length=20,
                            choices=[
                                  ('cheque', 'Cheque'),
                                  ('savings', 'Savings'),
                                  ('transmission', 'Transmission'),
                              ],
                            null=True, blank=True
                          )
    account_last_four = models.CharField(max_length=4, null=True, blank=True)  # display only

    # PayFast
    payfast_merchant_id = models.CharField(max_length=100, null=True, blank=True)
    payfast_merchant_key = models.CharField(max_length=100, null=True, blank=True)
    banking_verified = models.BooleanField(default=False)
    banking_submitted_at = models.DateTimeField(null=True, blank=True)

    # Payout config, this will allow us to manage how often we pay out the station owners and ensure we have the necessary information before processing payouts
    payout_schedule = models.CharField(max_length=20,choices=PAYOUT_SCHEDULE,default='weekly')

    # Financials
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_paid_out = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Referral tracking, meaning we can track how many users have signed up through this owner's referral link and how many clicks it has received
    # This can help us incentivize owners to promote the platform and reward them for bringing in new users.
    total_referral_clicks = models.PositiveIntegerField(default=0)

    # Listing tier (monetisation)
    listing_tier = models.CharField(max_length=20, choices=LISTING_TIER, default='free')
    tier_expires_at = models.DateTimeField(null=True, blank=True)

    # Audit + POPIA compliance
    popia_consent = models.BooleanField(default=False)
    popia_consent_at = models.DateTimeField(null=True, blank=True)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    banking_details_updated_at = models.DateTimeField(null=True, blank=True)
    banking_details_updated_by_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    #properties and methods for business logic
    @property #this will help us determine if the owner has provided all the necessary banking details for payouts
    def has_banking_details(self):
        return all([self.bank_name, self.account_number, self.branch_code])

    @property
    #the following function will help us determine if the owner is eligible for payout based on their verification status, banking details and pending payout amount
    def is_payout_eligible(self):
        return (

            self.verification_status == 'verified'
            and self.has_banking_details
            and self.pending_payout > 0
        )

    @property
    def station_count(self):
        return self.user.owened_stations.filter(is_active=True).count()

    def save(self, *args, **kwargs):
        #Always keep last four in sync
        if self.account_number:
            self.account_last_four = str(self.account_number)[-4:]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"


#This class will help us manage the payouts to station owners, 
# track the status of each payout and ensure we have all the necessary information for auditing and financial reporting purposes.
class OwnerPayout(models.Model):
    
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('processing', 'Processing'),
        ('completed',  'Completed'),
        ('failed',     'Failed'),
    ]

    owner = models.ForeignKey(StationOwnerProfile,on_delete=models.CASCADE,related_name='payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_deducted = models.DecimalField(max_digits=10, decimal_places=2)
    gross_bookings = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    period_start = models.DateField()
    period_end = models.DateField()

    # PayFast payout reference
    gateway_reference = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Exactly which bookings were included in this payout
    bookings = models.ManyToManyField('Booking',related_name='payout',blank=True)

    def __str__(self):
        return f"Payout {self.id} — {self.owner.business_name} — R{self.amount} ({self.status})"




class ChargingPoint(models.Model):
    STATUS_CHOICES = [
        ('info_only', 'Info Only'), #visible but not bookable
        ('claimed', 'Claimed'), # owner exists, not yet approved
        ('bookable', 'Bookable'), # owner exists, approved and bookable
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='owened_stations')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='info_only')
    commission_rate = models.DecimalField(max_digits=5,decimal_places=2,default=10.00) #percentage commission
    name = models.CharField(max_length=150, unique=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    capicity = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    address = models.CharField(max_length=255, default="Unknown address")
    availability = models.BooleanField(null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    off_peak_start = models.TimeField(null=True, blank=True)
    off_peak_end = models.TimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='charging_points_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='charging_points_updated')
    is_verified = models.BooleanField(default=False) #Only i the admin can verify a charging point
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    opening_hours = models.JSONField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True) # This will help us track when we last updated the station's availability and pricing from the external API

    connector_types = models.JSONField(null=True, blank=True,help_text="e.g. ['CCS2', 'Type2']")
    charging_speed_kw = models.PositiveIntegerField(null=True, blank=True,help_text="Max charging speed in kW")
    booking_url = models.URLField(null=True, blank=True,help_text="Owner's own booking page used for redirect model")
    amenities = models.JSONField(null=True, blank=True,help_text="e.g. ['coffee shop', 'mall', 'restrooms']")
    photos = models.JSONField(null=True, blank=True,help_text="List of uploaded photo URLs")

    def __str__(self):
        return f"{self.name} ({self.address})"


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


    def __str__(self):
        return f"Session made by {self.user} at {self.station} - {self.status}"



class Booking(models.Model):
    class Meta:
        unique_together = ('user', 'station', 'start_time', 'end_time')

    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    station = models.ForeignKey(ChargingPoint, on_delete=models.CASCADE)
    booking_date = models.DateField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    source = models.CharField(max_length=50,default='platform') #This ensures we know where the booking came from
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bookings_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bookings_updated')

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    platform_commission  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    owner_earnings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_out = models.BooleanField(default=False) #this field is for internal tracking of whether the owner has been paid out for this booking,
    paid_out_at = models.DateTimeField(null=True, blank=True)

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

    platform_commission = models.DecimalField(max_digits=10,decimal_places=2,default=0.0) #This is to track platform commission on each payment method
    station_earnings = models.DecimalField(max_digits=10,decimal_places=2,default=0.0) #This is to track station earnings on each payment method

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
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    platform_commission = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    station_earnings = models.DecimalField(max_digits=10,decimal_places=2,default=0)

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
    comment_text = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ratings_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ratings_updated')

    # This method ensures rating is between 1 and 5 or raises validation error
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
    comment_text = models.CharField(max_length=1000)
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


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Post: {self.title} by {self.author}"
    

#managing subscription plans for users
#this will help in managing the subscription plans for users
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_days = models.DurationField()
    features = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} - {self.price} for {self.duration_in_days} days"
    

#now tracking which station owners are subscribed to which plan
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
