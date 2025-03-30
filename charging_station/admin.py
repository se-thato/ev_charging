from django.contrib import admin
from .models import ChargingPoint, ChargingSession, Booking, Profile, PaymentMethods, Rating, IssueReport, Comment


admin.site.register(ChargingPoint)

admin.site.register(ChargingSession)

admin.site.register(Booking)

admin.site.register(Profile)

admin.site.register(PaymentMethods)

admin.site.register(Rating) 

admin.site.register(IssueReport)    

admin.site.register(Comment)
