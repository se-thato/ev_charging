from rest_framework import serializers
from .models import (ChargingPoint, ChargingSession, Booking, Profile, PaymentMethod,
                    Payment, Rating, IssueReport, Comment, SubscriptionPlan, 
                    UserSubscription, ChargingStationAnalitics, Post, StationOwnerProfile)
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account import app_settings as allauth_account_settings


# Custom serializer for user registration
class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(
        required=True
    )


class ChargingPointSerializer(serializers.ModelSerializer):
     # This field will be populated with the distance from the user to the charging point
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = ChargingPoint
        fields = '__all__'
        read_only_fields = ["id", "owner", "owner_username",
                             "name", "location", "address", "status",
                             "is_active", "is_verified", "capacity", "available_slots", "availability",
                             "price_per_hour", "booking_url", "connector_types", "charging_speed_kW",
                             "photos", "created_at", "distance"]
        


class StationOwnerProfileSerializer(serializers.ModelSerializer):
    #user = UserSerializer(read_only=True)
    station_count = serializers.SerializerMethodField()
    is_payout_eligible = serializers.SerializerMethodField()

    class Meta:
        model  = StationOwnerProfile
        fields = [
            'id', 'user', 'business_name', 'business_reg_number',
            'vat_number', 'phone_number', 'logo',
            'verification_status', 'verified_at',
            # banking — write_only means submit but never returned
            'bank_name', 'account_holder',
            'account_number',   # write_only field
            'branch_code',      # write_only
            'account_type', 'account_last_four',
            'banking_verified', 'banking_submitted_at',
            'payout_schedule', 'listing_tier', 'tier_expires_at',
            'pending_payout', 'total_earnings', 'total_paid_out',
            'total_referral_clicks',
            'popia_consent', 'popia_consent_at',
            'terms_accepted', 'terms_accepted_at',
            'station_count', 'is_payout_eligible',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'verified_at', 'account_last_four',
            'banking_verified', 'banking_submitted_at',
            'total_earnings', 'total_paid_out',
            'pending_payout', 'total_referral_clicks',
            'created_at', 'updated_at',
        ]
        extra_kwargs = {
            'account_number': {'write_only': True},
            'branch_code':    {'write_only': True},
        }

    #return number of stations owned by this user, used in the station owner dashboard to show how many stations they have listed
    def get_station_count(self, obj):
        return obj.station_count

    def get_is_payout_eligible(self, obj):
        return obj.is_payout_eligible




class ChargingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingSession
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'location', 'profile_picture']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'payment_type', 'last_four_digits', 'is_default']
        read_only_fields = ['id', 'last_four']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['status', 'gateway_response']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class IssueReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueReport
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription 
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active']


class ChargingStationAnaliticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingStationAnalitics
        fields = ['station', 'total_sessions', 'total_energy_consumed', 'total_revenue']