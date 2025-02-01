from django.conf.urls.static import static
from django.urls import path

from Web_Satellite_Tracking import settings
from .controllers.about import about
from .controllers.add_GS import add_ground_station, edit_ground_station
from .controllers.home import home
from .controllers.mission_plan import mission_plan
from .controllers.notifications import notifications
from .controllers.predictions import predictions
from .controllers.ground_station import ground_station, GroundStationListView
from .controllers.profile import profile, security
from .controllers.satellites import satellites_view, update_satellite, delete_satellite, fetch_satellites, \
    add_satellite, SatelliteTLEListView, fetch_satellites_from_url
from .controllers.storage import storage, SatellitePassListView
from .controllers.telemetry import telemetry, TelemetryAPIView
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('registration/', views.register, name='register'),
    path('logout/', views.logoutUser, name='logout'),

    path('profile/', profile, name="profile"),
    path('security/', security, name="security"),

    path('', home, name="home"),
    path('predictions/', predictions, name="predictions"),
    path('telemetry/', telemetry, name="telemetry"),
    path('mission_plan/', mission_plan, name="mission_plan"),
    path('storage/', storage, name="storage"),
    path('settings/ground_station/', ground_station, name="ground_station"),
    path('settings/satellites/', satellites_view, name="satellites"),
    path('settings/notifications/', notifications, name="notifications"),
    path('settings/about/', about, name="about"),

    path('add_ground_station/', add_ground_station, name='add_ground_station'),
    path("ground_station/<int:pk>/edit/", edit_ground_station, name="edit_ground_station"),

    path('fetch_satellites/', fetch_satellites, name='fetch_satellites'),
    path('fetch_satellites_from_url/', fetch_satellites_from_url, name='fetch_satellites_from_url'),
    path('add_satellite/', add_satellite, name='add_satellite'),
    path('update_satellite/', update_satellite, name='update_satellite'),
    path('delete_satellite/', delete_satellite, name='delete_satellite'),

    path('api/ground_stations/', GroundStationListView.as_view(), name='ground_stations'),
    path('api/satellites/', SatelliteTLEListView.as_view(), name='satellite_list'),
    path('api/satellite_passes/', SatellitePassListView.as_view(), name='satellite_pass_list'),
    path('api/telemetry/', TelemetryAPIView.as_view(), name='telemetry_api'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)