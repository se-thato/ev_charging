from django.shortcuts import render
from rest_framework import generics
from .models import ChargingPoint, Reservation
from .serializers import ChargingPointSerializer, ReservationSerializer

from django.http import JsonResponse
import geopy.distance


#charging points views 
class ChargingPointListCreateView(generics.ListCreateAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer


class ChargingPointDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer

    def Show_nearby_charging_points(request):
        user_latitude = float(request.GET.get('latitude', 0))
        user_longitude = float(request.GET.get('longitude', 0))
        radius = 10 

        charging_points = []
        for point in ChargingPoint.objects.all():
            distance = geopy.distance.geodesic((user_latitude, user_longitude), (point.latitude, point.longitude)).km

            if distance <= radius:
                charging_points.append({'name': point.name, 'location': point.location, 'latitude': point.latitude, 'longitude': point.longitude,
                'availability': point.availability})

        return JsonResponse ({'charging_points': charging_points})



#Reservations Views
class ReservationListCreateView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class ReserveDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

