# satellite_tracker/models.py
from django.db import models
from django.utils import timezone


class SatelliteTLE(models.Model):
    TLE_GROUP_CHOICES = [
        ('active', 'Active Satellites'),
        ('analyst', 'Analyst Satellites'),
        ('cubesat', 'CubeSats'),
        ('debris', 'Debris'),
        ('education', 'Education'),
        ('engineering', 'Engineering'),
        ('earthobs', 'Earth Observation'),
        ('galileo', 'Galileo'),
        ('geo', 'Geostationary'),
        ('glo-ops', 'GLONASS Operational'),
        ('glo-all', 'GLONASS All'),
        ('gps-ops', 'GPS Operational'),
        ('gps-all', 'GPS All'),
        ('geo-protected', 'Geostationary Protected Region'),
        ('geo-unregistered', 'Geostationary Unregistered'),
        ('intelsat', 'Intelsat Satellites'),
        ('iridium', 'Iridium Satellites'),
        ('military', 'Military Satellites'),
        ('other', 'Other Satellites'),
        ('planet', 'Planet Satellites'),
        ('science', 'Science Satellites'),
        ('stations', 'Stations'),
        ('starlink', 'Starlink'),
        ('tdrss', 'TDRSS'),
        ('weather', 'Weather Satellites')
    ]
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    line1 = models.CharField(max_length=70, null=True, blank=True)
    line2 = models.CharField(max_length=70, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    auto_tracking = models.BooleanField(default=False, help_text="Whether auto-tracking is enabled for this satellite.")
    orbit_status = models.CharField(
        max_length=20,
        choices=[('orbiting', 'Orbiting'), ('de-orbited', 'De-orbited')],
        default='orbiting',
        help_text="The orbit status of the satellite."
    )
    tle_group = models.CharField(
        max_length=20,
        choices=TLE_GROUP_CHOICES,
        default='weather',
        help_text="The TLE group from CelesTrak used for updating TLE data."
    )

    class Meta:
        db_table = 'Satellites'
        # This ensures no two entries have the same satellite_name and pass_time
        unique_together = ('name', 'line1', 'line2')

    def __str__(self):
        return self.name

    def get_tle_update_url(self):
        base_url = 'https://celestrak.org/NORAD/elements/gp.php'
        return f"{base_url}?GROUP={self.tle_group}&FORMAT=tle"
