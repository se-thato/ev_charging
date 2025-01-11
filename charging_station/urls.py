from django.urls import path
from .views import ChargingPointListCreateView, ChargingPointDetailView, ReservationListCreateView, ReserveDetailView

urlpatterns = [
    path('stations_list/', ChargingPointListCreateView.as_view(), name="stations_list"),
    path('stations/<int:pk>/', ChargingPointDetailView.as_view(), name="stations_details"), 
    #Reservations 
    path('reservations/', ReservationListCreateView.as_view(), name ="reservations"),
    path('reservations/<int:pk>/', ReserveDetailView.as_view(), name="reservations_details"),
]
