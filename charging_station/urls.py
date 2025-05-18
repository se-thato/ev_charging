from django.contrib.auth import views as auth_views
from django.shortcuts import render

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
SubscriptionPlanListCreateView,
SubscriptionPlanDetailView,
UserSubscriptionCreateListView,
ChargingStationAnaliticsCreateListView,
ChargingStationAnalyticsView,
)





urlpatterns = [
    path('stations-list/', ChargingPointListCreateView.as_view(), name="stations-list"),
    path('stations_list_details/<int:pk>/', ChargingPointDetailView.as_view(), name="stations_list_details"), 
  

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

    #reset password
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="VoltHub/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="VoltHub/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="VoltHub/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="VoltHub/password_reset_done.html"), name="password_reset_complete"),

    #subscription plan
    path('subscription_plans/', SubscriptionPlanListCreateView.as_view(), name="subscription_plans"),
    path('subscription_plans/<int:pk>/', SubscriptionPlanDetailView.as_view(), name="subscription_plans_details"),
    path('user_subscription/', UserSubscriptionCreateListView.as_view(), name="user_subscription"),

    #charging station analytics
    path('charging_station_analytics/', ChargingStationAnaliticsCreateListView.as_view(), name="charging_station_analytics"),
    path('analytics/', ChargingStationAnalyticsView.as_view(), name='charging-station-analytics'),

   
]
