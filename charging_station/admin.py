from django.contrib import admin
from .models import ChargingPoint, ChargingSession


admin.site.register(ChargingPoint)

admin.site.register(ChargingSession)
