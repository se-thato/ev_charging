
# ─────────────────────────────────────────────────────────────────────────────
# This file has two consumers:
#
# 1. AnalyticsConsumer (already existed) — left unchanged
# 2. StationStatusConsumer (new) — broadcasts live station status updates
#
# HOW WEBSOCKETS WORK IN DJANGO CHANNELS:
#
#   Browser opens:  ws://localhost:8000/ws/stations/
#   Django routes:  → StationStatusConsumer
#   Consumer joins: → channel group "station_updates"
#   When status changes anywhere in Django:
#     → channel_layer.group_send("station_updates", {...})
#     → Consumer receives it and sends to browser
#     → Browser updates sidebar/markers instantly
# ─────────────────────────────────────────────────────────────────────────────

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from charging_station.models import ChargingPoint


class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    async def disconnect(self, close_code):
        pass
    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps(data))


class StationStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that sends live station status updates to the browser.

    Every connected browser tab joins the "station_updates" group.
    When any station changes (available_slots, status, etc.), Django
    calls channel_layer.group_send() which this consumer receives and
    immediately forwards to the browser.

    The browser then updates the sidebar and map markers without refresh.
    """

    # All connected clients share this group name
    # so a single broadcast reaches every browser tab
    GROUP_NAME = 'station_updates'

    async def connect(self):
        # Join the shared broadcast group
        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )
        await self.accept()

        # Send current station snapshot immediately on connect
        # so the sidebar populates before any update event fires
        snapshot = await self.get_station_snapshot()
        await self.send(text_data=json.dumps({
            'type': 'snapshot',
            'stations': snapshot,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )

    async def receive(self, text_data):
        # Browser can send {type: "ping"} to keep connection alive
        # We don't need to handle anything else from the client
        pass

    async def station_update(self, event):
        """
        Called by channel_layer.group_send() when a station changes.
        Forwards the update to the browser.

        event shape (sent from views/signals):
        {
            "type": "station_update",
            "station": {
                "id": 1,
                "name": "VoltHub Station 1",
                "status": "online",
                "available_slots": 3,
                "total_slots": 5
            }
        }
        """
        await self.send(text_data=json.dumps({
            'type': 'station_update',
            'station': event['station'],
        }))

    @database_sync_to_async
    def get_station_snapshot(self):
        """
        Returns all verified, active stations as a list of dicts.
        Called once on WebSocket connect to populate the sidebar immediately.
        database_sync_to_async wraps the synchronous ORM call so it
        can be awaited in the async WebSocket consumer.
        """
       
        stations = ChargingPoint.objects.filter( 
            is_verified=True,
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False,
        ).values(
            'id', 'name', 'address', 'location',
            'latitude', 'longitude',
            'available_slots', 'capacity',
            'availability', 'status',
            'price_per_hour', 'opening_hours',
        )

        result = []
        for s in stations:
            # Calculate live status
            if s['available_slots'] == 0:
                live_status = 'full'
            elif s['availability']:
                live_status = 'online'
            else:
                live_status = 'offline'

            result.append({
                'id': s['id'],
                'source': 'volthub',
                'name': s['name'],
                'address': s['address'] or s['location'],
                'lat': float(s['latitude']),
                'lng': float(s['longitude']),
                'status': live_status,
                'available_slots': s['available_slots'],
                'total_slots': s['capicity'],
                'price_per_hour': str(s['price_per_hour']) if s['price_per_hour'] else None,
                'opening_hours': s['opening_hours'],
                'bookable': s['status'] == 'bookable',
            })

        return result