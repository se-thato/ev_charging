from rest_framework import serializers
from .models import ChargingPoint, ChargingSession, Booking

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
