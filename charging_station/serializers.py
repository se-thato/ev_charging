from rest_framework import serializers
from .models import ChargingPoint, ChargingSession, Booking, Profile, PaymentMethod, Payment, Rating, IssueReport, Comment, SubscriptionPlan, UserSubscription, ChargingStationAnalitics
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
        read_only_fields = ["owner", "is_verified", "created_at", "distance"]



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