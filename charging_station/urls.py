from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    ChargingPointViewSet,
    ChargingSessionViewSet,
    BookingViewSet,
    ProfileViewSet,
    PaymentMethodViewSet,
    PaymentViewSet,
    RatingViewSet,
    IssueReportViewSet,
    CommentViewSet,
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
    ChargingStationAnaliticsViewSet,
    PostViewSet,
)

urlpatterns = [
    # charging points
    path(
        "stations-list/",
        ChargingPointViewSet.as_view({"get": "list", "post": "create"}),
        name="stations-list",
    ),
    path("stations_list_details/<int:pk>/",ChargingPointViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="stations_list_details",
    ),

    # charging sessions
    path(
        "charging-sessions/",
        ChargingSessionViewSet.as_view({"get": "list", "post": "create"}),
        name="charging_session",
    ),
    path(
        "charging-sessions/<int:pk>/",
        ChargingSessionViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="charging_sessions_details",
    ),

    # bookings
    path(
        "bookings/",
        BookingViewSet.as_view({"get": "list", "post": "create"}),
        name="bookings",
    ),
    path(
        "bookings/<int:pk>/",
        BookingViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="bookings_details",
    ),

    # profile (collection only per original urls)
    path(
        "profiles/",
        ProfileViewSet.as_view({"get": "list", "post": "create"}),
        name="profiles",
    ),

    # payment section (collection only per original urls)
    path(
        "payment-method/",
        PaymentMethodViewSet.as_view({"get": "list", "post": "create"}),
        name="payment-method",
    ),
    path(
        "payment/",
        PaymentViewSet.as_view({"get": "list", "post": "create"}),
        name="payment",
    ),

    # rating (collection only)
    path(
        "ratings/",
        RatingViewSet.as_view({"get": "list", "post": "create"}),
        name="ratings",
    ),

    # issue report (collection only)
    path(
        "issue-reports/",
        IssueReportViewSet.as_view({"get": "list", "post": "create"}),
        name="issue_reports",
    ),
    

    # comments (collection only)
    path(
        "comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="comments",
    ),
     
     path(
        "comments/<int:pk>",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="comments_details",
    ),

    # post
    path(
        "posts/<int:pk>/",
        PostViewSet.as_view({"get": "retrieve"}),
        name="posts_details",
    ),

    # subscription plan
    path(
        "subscription_plans/",
        SubscriptionPlanViewSet.as_view({"get": "list", "post": "create"}),
        name="subscription_plans",
    ),
    path(
        "subscription_plans/<int:pk>/",
        SubscriptionPlanViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="subscription_plans_details",
    ),
    path(
        "user_subscription/",
        UserSubscriptionViewSet.as_view({"get": "list", "post": "create"}),
        name="user_subscription",
    ),

    # charging station analytics
    path("charging_station_analytics/",
        ChargingStationAnaliticsViewSet.as_view({"get": "list", "post": "create"}),
        name="charging_station_analytics",
    ),
    # Keep the extra analytics alias, mapped to the same list action
    path("analytics/",ChargingStationAnaliticsViewSet.as_view({"get": "list"}),name="charging-station-analytics",),
]