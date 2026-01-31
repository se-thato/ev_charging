from django.urls import path
from . import views


urlpatterns = [
    path('user_dashboard', views.dashboard, name="user_dashboard"),
    path('station_owner_dashboard', views.station_owner_dashboard, name="station_owner_dashboard"),
]