from rest_framework import serializers
from .models import ChargingPoint, ChargingSession, Booking, Profile, PaymentMethods

class ChargingPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChargingPoint
        fields = ['__all__']



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


class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethods
        fields = '__all__'