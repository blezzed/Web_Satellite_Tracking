from django.contrib import admin

from main.entities.chats_modal import ChatMessage
from main.entities.ground_station import GroundStation
from main.entities.mission_plan import MissionPlan
from main.entities.profile import UserProfile
from main.entities.sat_pass import SatellitePass
from main.entities.telemetry import TelemetryModel
from main.entities.tle import SatelliteTLE

# Register your models here.
admin.site.register(SatelliteTLE)
admin.site.register(SatellitePass)
admin.site.register(TelemetryModel)
admin.site.register(GroundStation)
admin.site.register(UserProfile)
admin.site.register(MissionPlan)
admin.site.register(ChatMessage)