from django.urls import path
from .controllers.home import home
from .controllers.predictions import predictions
from .controllers.storage import storage
from .controllers.telemetry import telemetry

urlpatterns = [
    path('', home, name="home"),
    path('predictions/', predictions, name="predictions"),
    path('telemetry/', telemetry, name="telemetry"),
    path('storage/', storage, name="storage"),
]
