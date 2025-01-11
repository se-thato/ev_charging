from django.contrib import admin
from .models import ChargingPoint, Reservation


admin.site.register(ChargingPoint)
admin.site.register(Reservation)
