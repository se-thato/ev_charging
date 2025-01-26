from django.contrib import admin
from .models import ChargingPoint, ChargingSession, Booking


admin.site.register(ChargingPoint)

admin.site.register(ChargingSession)

admin.site.register(Booking)
