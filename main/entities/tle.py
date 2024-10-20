# satellite_tracker/models.py
from django.db import models
from django.utils import timezone


class SatelliteTLE(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    line1 = models.CharField(max_length=70)
    line2 = models.CharField(max_length=70)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
