from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("charging_station.urls")),
    path('', include("VoltHub.urls")),
    path('', include("authentication.urls")),
    #authentication
    path('auth', include('authentication.urls')),
]
