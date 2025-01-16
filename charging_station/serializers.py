from rest_framework import serializers
from .models import ChargingPoint, Reservation, ChargingSession

class ChargingPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChargingPoint
        fields = ['id', 'name', 'capicity', 'available_slots', 'location', 'latitude', 'longitude']

class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = '__all__'


class ChargingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingSession
        fields = '__all__'
