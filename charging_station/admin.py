from django.contrib import admin
from .models import ChargingPoint, ChargingSession, Booking, Profile, PaymentMethod, Rating, IssueReport, Comment, Payment, SubscriptionPlan, UserSubscription


admin.site.register(ChargingPoint)

admin.site.register(ChargingSession)

admin.site.register(Booking)

admin.site.register(Profile)

admin.site.register(PaymentMethod)

admin.site.register(Rating) 

admin.site.register(IssueReport)    

admin.site.register(Comment)

admin.site.register(Payment)

admin.site.register(SubscriptionPlan)   

admin.site.register(UserSubscription)
