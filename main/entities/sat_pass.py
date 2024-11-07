# main/entities/satellite_pass.py
from django.db import models
from django.utils import timezone


class SatellitePass(models.Model):
    satellite_name = models.CharField(max_length=255)
    rise_pass_time = models.DateTimeField(null=True, blank=True)
    set_pass_time = models.DateTimeField()
    max_elevation = models.FloatField()
    azimuth = models.FloatField()
    distance = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This ensures no two entries have the same satellite_name and pass_time
        unique_together = ('satellite_name', 'rise_pass_time', 'set_pass_time')

    def __str__(self):
        return f"{self.satellite_name} at {self.rise_pass_time}-{self.set_pass_time}"
