from django.urls import re_path
from .consumers import AnalyticsConsumer, StationStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/analytics/$', AnalyticsConsumer.as_asgi()), 

    # live station status WebSocket
    # Browser connects to: ws://localhost:8000/ws/stations/
    re_path(r'ws/stations/$', StationStatusConsumer.as_asgi()),
]