# satellite_tracker/models.py
from django.db import models
from django.utils import timezone


class SatelliteTLE(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    line1 = models.CharField(max_length=70, null=True, blank=True)
    line2 = models.CharField(max_length=70, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This ensures no two entries have the same satellite_name and pass_time
        unique_together = ('name', 'line1', 'line2')

    def __str__(self):
        return self.name
