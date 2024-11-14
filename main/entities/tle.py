# satellite_tracker/models.py
from django.db import models
from django.utils import timezone


class SatelliteTLE(models.Model):
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

    class Meta:
        # This ensures no two entries have the same satellite_name and pass_time
        unique_together = ('name', 'line1', 'line2')

    def __str__(self):
        return self.name
