# main/entities/satellite_pass.py
from django.db import models
from django.utils import timezone


class SatellitePass(models.Model):
    satellite_name = models.CharField(max_length=255)
    pass_time = models.DateTimeField()  # Time when the satellite pass occurs
    max_elevation = models.FloatField()  # Maximum elevation during the pass
    azimuth = models.FloatField()  # Azimuth direction during the pass
    distance = models.FloatField()  # Distance from ground station during the pass
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This ensures no two entries have the same satellite_name and pass_time
        unique_together = ('satellite_name', 'pass_time')

    def __str__(self):
        return f"{self.satellite_name} at {self.pass_time}"
