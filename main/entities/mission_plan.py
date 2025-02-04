from django.contrib.gis.db import models


class MissionPlan(models.Model):
    # Latitude and longitude for the ground station or mission location
    location = models.PointField( null=True)

    # Selected pass details
    rise_time = models.DateTimeField()
    set_time = models.DateTimeField()
    max_elevation = models.FloatField()  # Maximum elevation during the pass (degrees)

    # Trajectory points: Array of [latitude, longitude] pairs
    trajectory = models.LineStringField( null=True)

    # Configuration fields
    orbiting_satellite = models.IntegerField()  # Reference to the satellite ID
    min_elevation = models.PositiveIntegerField(default=10)  # Minimum elevation allowed (degrees)
    prediction_days = models.PositiveIntegerField(default=5)  # Prediction range in days
    sun_illumination = models.BooleanField(default=False)  # Whether to limit to sun-illuminated passes

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Mission Plan'
        ordering = ['-created_at']

    def __str__(self):
        return f"Mission Plan ({self.location.y}, {self.location.x}) - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"