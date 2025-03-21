from django.urls import path
from .views import ( 
ChargingPointListCreateView,
ChargingPointDetailView,
ChargingSessionListCreateView,
ChargingSessionDetailView,
BookingListCreateView,
ProfileListCreateView,
PaymentMethods
#show_nearby_charging_points
)


urlpatterns = [
    path('stations_list/', ChargingPointListCreateView.as_view(), name="stations_list"),
    path('stations/<int:pk>/', ChargingPointDetailView.as_view(), name="stations_details"), 
  

    path('charging_sessions/', ChargingSessionListCreateView.as_view(), name ="charging_session"),
    path('charging_sessions/<int:pk>/', ChargingSessionDetailView.as_view(), name="charging_sessions_details"),
    
    #bookings
    path('Booking/', BookingListCreateView.as_view(), name="Booking"),
    path('Booking/<int:pk>/', BookingListCreateView.as_view(), name="Booking_details"),

    #profile
    path('Profile/', ProfileListCreateView.as_view(), name="Profile"),

    #payment section
    path('Payment/', PaymentMethods.as_view(), name="Payment"),

    #charging points
    #path('show_nearby_charging_points', show_nearby_charging_points, name="show_nearby_charging_points"),
    
]
