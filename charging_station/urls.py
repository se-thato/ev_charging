from django.urls import path
from .views import ( 
ChargingPointListCreateView,
ChargingPointDetailView,
ChargingSessionListCreateView,
ChargingSessionDetailView,
BookingListCreateView,
BookingDetailView,
ProfileListCreateView,
PaymentMethodListCreateView,
PaymentListCreateView,
RatingListCreateView,
IssueReportListCreateView,
CommentListCreateView,

)


urlpatterns = [
    path('stations-list/', ChargingPointListCreateView.as_view(), name="stations_list"),
    path('stations-list/<int:pk>/', ChargingPointDetailView.as_view(), name="stations_list_details"), 
  

    path('charging-sessions/', ChargingSessionListCreateView.as_view(), name ="charging_session"),
    path('charging-sessions/<int:pk>/', ChargingSessionDetailView.as_view(), name="charging_sessions_details"),
    
    #bookings
    path('bookings/', BookingListCreateView.as_view(), name="bookings"),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name="bookings_details"),

    #profile
    path('profiles/', ProfileListCreateView.as_view(), name="profiles"),

    #payment section
    path('payment-method/', PaymentMethodListCreateView.as_view(), name="payment-method"),
    path('payment/', PaymentListCreateView.as_view(), name="payment"),

    #rating
    path('ratings/', RatingListCreateView.as_view(), name="ratings"),

    #issue report
    path('issue-reports/', IssueReportListCreateView.as_view(), name="issue_reports"),

    #comments
    path('comments/', CommentListCreateView.as_view(), name="comments"),

]
