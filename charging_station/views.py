from django.shortcuts import render
from rest_framework import generics
from .models import ChargingPoint, ChargingSession, Booking, Profile
from .serializers import ChargingPointSerializer, ChargingSessionSerializer, BookingSerializer, ProfileSerializer

from rest_framework.filters import SearchFilter, OrderingFilter

from django.http import JsonResponse
import geopy.distance

from rest_framework.decorators import api_view
from rest_framework.response import Response



#charging points views 
class ChargingPointListCreateView(generics.ListCreateAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer

    #search filter
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = []

    

class ChargingPointDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer



#charging session 
class ChargingSessionListCreateView(generics.ListCreateAPIView):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer


    @api_view(['GET'])
    def get_available_slots(request, station_id):
        try:
            station = ChargingPoint.objects.get(id=station_id)
            now_time = now()
            available_sessions = ChargingSession.objects.filter(station=station, start_time__gte=now_time, status='Scheduled')
            serializer = ChargingSessionSerializer(available_sessions, many=True)

            return Response(serializer.data)
        except ChargingPoint.DoesNotExist:
            return Response({"error": "Ohh No! Station Not Found"}, 
            status= status.HTTP_404_NOT_FOUND)


    @api_view(['POST'])
    def book_charging_sessions(request):
        user = request.user
        station_id = request.data.get("station_id")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        try:
            station = ChargingPoint.objects.get(id=station_id)
            cost = calculate_cost(station, start_time, end_time)

            #checking if the slots are available
            overlapping_sessions = ChargingSession.objects.filter(station=station, start_time__lt=end_time, end_time__gt=start_time, status='Scheduled')

            if overlapping_sessions.exists():
                return Response({"error": "Time slot is running out."}, status=status.HTTP_400_BAD_REQUEST)

            session = ChargingSession.objects.create(
                user =user,
                station = station,
                start_time = start_time,
                end_time = end_time,
                cost = cost
            )

            serializer = chargingSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ChargingPoint.DoesNotExist:
            return Response({"error": "Station Not Found"}, status=status.HTTP_404_NOT_FOUND)

    
class ChargingSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer


    @api_view(['DELETE'])
    def cancel_session(request, session_id):
        try:
            session = ChargingSession.objects.get(id_session_id, user=request.user)
            session.status = "Cancelled"
            session.save()
            return Response({"message": "The Session Has Been Cancelled Successfully."}, status=status.HTTP_200_OK)

        except ChargingSession.DoesNotExist:
            return Response({"error": " Session Not Found Or You Don't Have Permission To Cancel It.."}, status=status.HTTP_404_NOT_FOUND)
        


class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


    def booking(request):

        serializer = BookingSerializer()
        if request.method == 'POST':
            serializer = BookingSerializer(request.POST)

            if serializer.is_valid():
                serializer.save()





class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer