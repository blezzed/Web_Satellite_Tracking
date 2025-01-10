from django.db import models

from main.entities.tle import SatelliteTLE


class TelemetryModel(models.Model):
    """
    Model to store telemetry data for satellites.
    """
    satellite = models.ForeignKey(
        SatelliteTLE,
        on_delete=models.CASCADE,
        related_name="telemetry_data",
        help_text="Reference to the satellite this telemetry data belongs to"
    )
    timestamp = models.DateTimeField(help_text="Time of the telemetry data recording")
    latitude = models.FloatField(help_text="Latitude of the satellite position in degrees")
    longitude = models.FloatField(help_text="Longitude of the satellite position in degrees")
    altitude = models.FloatField(help_text="Altitude of the satellite above Earth in kilometers")
    velocity = models.FloatField(help_text="Velocity of the satellite in kilometers per second")
    health_status = models.CharField(
        max_length=20,
        choices=[
            ('Nominal', 'Nominal'),
            ('Warning', 'Warning'),
            ('Critical', 'Critical'),
        ],
        default='Nominal',
        help_text="Health status of the satellite"
    )
    battery_voltage = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Battery voltage in volts"
    )
    solar_panel_status = models.BooleanField(
        default=True, 
        help_text="Whether the solar panel is operational"
    )
    temperature = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Internal temperature of the satellite in Celsius"
    )
    signal_strength = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Signal strength in dBm"
    )
    pitch = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Pitch angle of the satellite in degrees"
    )
    yaw = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Yaw angle of the satellite in degrees"
    )
    roll = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Roll angle of the satellite in degrees"
    )
    power_consumption = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Power consumption in watts"
    )
    data_rate = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Data transfer rate in Mbps"
    )
    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Error code or anomaly detected"
    )
    command_status = models.CharField(
        max_length=20,
        choices=[
            ('Idle', 'Idle'),
            ('Executing', 'Executing'),
            ('Completed', 'Completed'),
            ('Failed', 'Failed'),
        ],
        default='Idle',
        help_text="Status of command execution"
    )
    additional_data = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Additional telemetry data in JSON format for extensibility"
    )

    def __str__(self):
        return f"Telemetry for {self.satellite} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Telemetry Data"
        verbose_name_plural = "Telemetry Data"
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['satellite']),
        ]
