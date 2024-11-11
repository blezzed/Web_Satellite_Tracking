from django.urls import path

from .controllers.about import about
from .controllers.add_GS import add_ground_station
from .controllers.home import home
from .controllers.predictions import predictions
from .controllers.ground_station import ground_station
from .controllers.satellites import satellites
from .controllers.storage import storage
from .controllers.telemetry import telemetry

urlpatterns = [
    path('', home, name="home"),
    path('predictions/', predictions, name="predictions"),
    path('telemetry/', telemetry, name="telemetry"),
    path('storage/', storage, name="storage"),
    path('settings/ground_station/', ground_station, name="ground_station"),
    path('settings/satellites/', satellites, name="satellites"),
    path('settings/about/', about, name="about"),

    path('add_ground_station/', add_ground_station, name='add_ground_station'),
]
