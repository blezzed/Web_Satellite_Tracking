# satellite_tracker/routing.py
from django.urls import path
from .consumer import sat_pass_consumer, sat_position_consumer

websocket_urlpatterns = [
    path('ws/satellite/', sat_position_consumer.SatelliteConsumer.as_asgi()),
    path('ws/satellite_passes/', sat_pass_consumer.SatellitePassConsumer.as_asgi()),
]