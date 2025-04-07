from rest_framework import serializers
from .models import ChargingPoint, ChargingSession, Booking, Profile, PaymentMethod, Payment, Rating, IssueReport, Comment

class ChargingPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChargingPoint
        fields = '__all__'



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
        fields = ['id', 'username', 'first_name', 'last_name']


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