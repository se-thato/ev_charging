from django.contrib import admin
from .models import ChargingPoint, Reservation, ChargingSession


admin.site.register(ChargingPoint)
admin.site.register(Reservation)
admin.site.register(ChargingSession)
