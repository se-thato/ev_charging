from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from charging_station.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'is_station_owner',
        'is_station_owner_verified',
    )

    list_filter = (
        'is_station_owner',
        'is_station_owner_verified',
    )

# Register the Profile admin only if it's not already registered by another app
try:
    admin.site.register(Profile, ProfileAdmin)
except AlreadyRegistered:
    # Profile was registered elsewhere (e.g., charging_station.admin). Do not re-register.
    pass

