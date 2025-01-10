from django.db import models

class GroundStation(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Unique name of the ground station")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude of the ground station in decimal degrees")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude of the ground station in decimal degrees")
    altitude = models.FloatField(help_text="Altitude of the ground station in meters above sea level")
    start_tracking_elevation = models.FloatField(
        default=10.0,  # A typical value for minimum tracking elevation
        help_text="Minimum elevation angle (in degrees) above horizon to start tracking"
    )
    is_active = models.BooleanField(default=True, help_text="Indicates if the ground station is active")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the ground station was added")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the ground station was last updated")

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"

    class Meta:
        db_table = 'Ground Station'
        verbose_name = "Ground Station"
        verbose_name_plural = "Ground Stations"
        unique_together = ('name', 'latitude', 'longitude')
