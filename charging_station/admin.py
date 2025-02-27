from django.contrib import admin
from .models import ChargingPoint, ChargingSession, Booking, Profile, PaymentMethods


admin.site.register(ChargingPoint)

admin.site.register(ChargingSession)

admin.site.register(Booking)

admin.site.register(Profile)

admin.site.register(PaymentMethods)
