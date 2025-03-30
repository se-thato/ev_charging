from django.urls import path
from .views import ( 
ChargingPointListCreateView,
ChargingPointDetailView,
ChargingSessionListCreateView,
ChargingSessionDetailView,
BookingListCreateView,
ProfileListCreateView,
PaymentMethods,
RatingListCreateView,
IssueReportListCreateView,
CommentListCreateView,

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

    #rating
    path('Rating/', RatingListCreateView.as_view(), name="Rating"),

    #issue report
    path('IssueReport/', IssueReportListCreateView.as_view(), name="IssueReport"),

    #comments
    path('Comments/', CommentListCreateView.as_view(), name="Comments"),

]
