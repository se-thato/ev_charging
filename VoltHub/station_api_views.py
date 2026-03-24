import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.cache import cache

from charging_station.models import ChargingPoint


@require_GET
def nearby_ocm_stations(request):
   
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse(
            {'error': 'lat and lng are required and must be numbers'},
            status=400
        )

    radius = float(request.GET.get('radius', 25))

    #Fetch from OpenChargeMap (with 5-minute cache)
    cache_key = f'ocm_stations_{lat:.3f}_{lng:.3f}_{radius}'
    ocm_data = cache.get(cache_key)

    if ocm_data is None: # No cached data, fetch fresh from OpenChargeMap
        try:
            api_key = settings.OPEN_CHARGE_API_KEY
            url = (
                f'https://api.openchargemap.io/v3/poi/'
                f'?output=json'
                f'&latitude={lat}'
                f'&longitude={lng}'
                f'&distance={radius}'
                f'&distanceunit=KM'
                f'&maxresults=100'
                f'&compact=true'
                f'&verbose=false'
                f'&key={api_key}'
            )
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            raw = response.json()

            # Clean up the response — only send what the frontend needs
            # This reduces payload size and hides unnecessary API details
            ocm_data = []
            for station in raw:
                addr = station.get('AddressInfo', {})
                connections = station.get('Connections', [])

                # Extract connector types
                connector_types = []
                for conn in connections:
                    ct = conn.get('ConnectionType', {})
                    if ct and ct.get('Title'):
                        connector_types.append(ct['Title'])

                # Determine online/offline status
                # StatusType: 0 = unknown, 50 = operational, 75 = partly operational,
                # 100 = not operational, 150 = planned
                status_type = station.get('StatusType', {}) or {}
                status_id = status_type.get('ID', 0)
                if status_id == 50:
                    status = 'online'
                elif status_id in (75,):
                    status = 'partial'
                elif status_id in (100, 200):
                    status = 'offline'
                else:
                    status = 'unknown'

                ocm_data.append({
                    'id': station.get('ID'),
                    'source': 'ocm',         # tells the frontend this is external
                    'name': addr.get('Title', 'Charging Station'),
                    'address': addr.get('AddressLine1', ''),
                    'lat': addr.get('Latitude'),
                    'lng': addr.get('Longitude'),
                    'status': status,
                    'usage_cost': station.get('UsageCost', 'N/A'),
                    'connector_types': list(set(connector_types)),
                    'num_points': station.get('NumberOfPoints'),
                })

            # Cache for 5 minutes (300 seconds)
            cache.set(cache_key, ocm_data, 300)

        except requests.Timeout:
            return JsonResponse({'error': 'OpenChargeMap request timed out'}, status=504)
        except requests.RequestException as e:
            return JsonResponse({'error': f'OpenChargeMap request failed: {str(e)}'}, status=502)

    # Fetching stations from Django DB
    # Only include verified, active stations that have coordinates
    our_stations_qs = ChargingPoint.objects.filter(
        is_verified=True,
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ).values(
        'id', 'name', 'location', 'address',
        'latitude', 'longitude',
        'available_slots', 'capicity',
        'availability', 'is_active',
        'price_per_hour', 'status',
        'off_peak_start', 'off_peak_end',
        'opening_hours',
    )

    our_stations = []
    for s in our_stations_qs:
        # Determine live status for sidebar display
        if not s['is_active']:
            live_status = 'offline'
        elif s['available_slots'] == 0:
            live_status = 'full'
        elif s['availability']:
            live_status = 'online'
        else:
            live_status = 'unknown'

        our_stations.append({
            'id': s['id'],
            'source': 'volthub',         # This tells the frontend this is from my db and not to expect OCM fields
            'name': s['name'],
            'address': s['address'] or s['location'],
            'lat': float(s['latitude']),
            'lng': float(s['longitude']),
            'status': live_status,
            'available_slots': s['available_slots'],
            'total_slots': s['capicity'],
            'price_per_hour': str(s['price_per_hour']) if s['price_per_hour'] else None,
            'opening_hours': s['opening_hours'],
            'off_peak_start': str(s['off_peak_start']) if s['off_peak_start'] else None,
            'off_peak_end': str(s['off_peak_end']) if s['off_peak_end'] else None,
            'bookable': s['status'] == 'bookable',
        })

    return JsonResponse({
        'ocm_stations': ocm_data,
        'our_stations': our_stations,
    })