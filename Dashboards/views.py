from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from Dashboards.permissions import station_owner_required
from charging_station.models import ChargingPoint, ChargingSession, Booking, Payment

from django.utils.timezone import now
from django.db.models import Sum


@login_required(login_url='authentication:login')
def dashboard(request):
    try:
        stations = ChargingPoint.objects.filter(is_active=True)  # olny active stations
        sessions = ChargingSession.objects.filter(user=request.user).select_related('station')
        bookings = Booking.objects.filter(user=request.user).select_related('station')  # This will fetch user specific bookings

        context = {
            'stations': stations,
            'sessions': sessions,
            'bookings': bookings,
        }
        return render(request, 'Dashboards/dashboard.html', context)

    except Exception as e:
        # 
        return HttpResponse(f"An error occurred: {str(e)}", status=500)



@login_required
@station_owner_required #This will ensure only station owners can access this view
def station_owner_dashboard(request):
    """
    This view renders the station owner dashboard.

    It is protected so that:
    - User must be logged in
    - User must own at least one charging station
    """

    user = request.user  # The currently logged-in user

    # STEP 1: Get all stations owned by this user
    # This is how we identify a "station owner"
    stations = ChargingPoint.objects.filter(owner=user)

    # STEP 2: Security check
    # If the user does NOT own any stations,
    # they are not allowed to access this dashboard
    if not stations.exists():
        return redirect("user_dashboard")  # fallback (or show 403 page)



    # STEP 3: Get bookings related ONLY to the owner's stations
    # station__in=stations ensures owners only see THEIR data
    bookings = Booking.objects.filter(station__in=stations).select_related("user", "station").order_by("-created_at")


    # STEP 4: Calculate monthly earnings
    # We sum completed payments related to the owner's stations
    current_month = now().month
    current_year = now().year

    monthly_earnings = Payment.objects.filter(
        charging_session__station__in=stations,
        status="completed",
        created_at__month=current_month,
        created_at__year=current_year
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0  # fallback to 0 if no payments exist

    # STEP 5: Count useful metrics (for dashboard cards)
    total_stations = stations.count()
    total_bookings = bookings.count()

    # Determine if the owner has any verified stations (set by decorator)
    owner_verified = getattr(request, 'station_owner_verified', False)

    # STEP 6: Send everything to the template
    context = {
        "stations": stations,
        "bookings": bookings[:20],  # only show recent 20 bookings
        "monthly_earnings": monthly_earnings,
        "total_stations": total_stations,
        "total_bookings": total_bookings,
        "owner_verified": owner_verified,
    }

    # STEP 7: Render the dashboard HTML
    return render(request,"Dashboards/station_owner.html",context)
