from django.shortcuts import render
from rest_framework import generics
from .models import ChargingPoint, Reservation
from .serializers import ChargingPointSerializer, ReservationSerializer


#charging points views 
class ChargingPointListCreateView(generics.ListCreateAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer


class ChargingPointDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer

#Reservations Views
class ReservationListCreateView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class ReserveDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

