# satellite_tracker/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/satellite/', consumers.SatelliteConsumer.as_asgi()),
]