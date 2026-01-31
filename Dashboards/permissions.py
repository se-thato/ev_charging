from django.core.exceptions import PermissionDenied

# This decorator ensures the user owns at least one ChargingPoint. It does
# not block access for unverified owners, but attaches a flag to the request
# so the view/template can display a notice and/or restrict actions.
def station_owner_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Avoid importing at module import time to prevent circular imports
        from charging_station.models import ChargingPoint

        user = request.user

        # Deny if user owns no stations at all
        stations_qs = ChargingPoint.objects.filter(owner=user)
        if not stations_qs.exists():
            raise PermissionDenied("You are not a station owner.")

        # Attach verification flag to the request for downstream use
        request.station_owner_verified = stations_qs.filter(is_verified=True).exists()

        return view_func(request, *args, **kwargs)

    return _wrapped_view
