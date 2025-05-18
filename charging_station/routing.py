from django.urls import re_path
from .consumers import AnalyticsConsumer

websocket_urlpatterns = [
    re_path(r'ws/analytics/$', AnalyticsConsumer.as_asgi()),
]
