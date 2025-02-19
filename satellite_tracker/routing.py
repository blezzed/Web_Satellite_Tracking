# satellite_tracker/routing.py
from django.urls import path, re_path
from .consumer import sat_pass_consumer, sat_position_consumer, sat_path_consumer
from .consumer.chat_consumer import ChatConsumer
from .consumer.telemetry_consumer import TelemetryConsumer

websocket_urlpatterns = [
    path('ws/satellite/', sat_position_consumer.SatelliteConsumer.as_asgi()),
    path('ws/satellite_path/', sat_path_consumer.SatellitePathConsumer.as_asgi()),
    path('ws/satellite_passes/', sat_pass_consumer.SatellitePassConsumer.as_asgi()),
    path("ws/telemetry/", TelemetryConsumer.as_asgi()),

    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]