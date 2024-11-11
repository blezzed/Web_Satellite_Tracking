from django.contrib import admin

from main.entities.ground_station import GroundStation
from main.entities.sat_pass import SatellitePass
from main.entities.tle import SatelliteTLE

# Register your models here.
admin.site.register(SatelliteTLE)
admin.site.register(SatellitePass)
admin.site.register(GroundStation)