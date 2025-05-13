import os
import asyncio

import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from webpush import send_user_notification, send_group_notification

from main.entities.tle import SatelliteTLE
from satellite_tracker.operations.values import BOT_TOKEN


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
        db_table = 'Telemetry Data'
        ordering = ['-timestamp']
        verbose_name = "Telemetry Data"
        verbose_name_plural = "Telemetry Data"
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['satellite']),
        ]

@receiver(post_save, sender=TelemetryModel)
def notify_new_telemetry(sender, instance, created, **kwargs):
    if created:
        payload = {
            "head": "Apogee",
            "body": f"Telemetry for {instance.satellite.name} has been added! \n Health: {instance.health_status}",
            "icon": "/static/assets/icons/dark_apogee.svg",
            "url": "/storage/"
        }

        send_group_notification(group_name="satellite_notifications", payload=payload, ttl=1000)


CHAT_ID_FILE_PATH = "../../repo/chat_id"

def get_chat_id():
    """Retrieve the chat ID from the file."""
    if os.path.exists(CHAT_ID_FILE_PATH):
        with open(CHAT_ID_FILE_PATH, "r", encoding="utf-16") as file:
            return file.read().strip()
    return None

def update_chat_id(new_chat_id):
    """Update the chat ID in the file."""
    os.makedirs(os.path.dirname(CHAT_ID_FILE_PATH), exist_ok=True)
    with open(CHAT_ID_FILE_PATH, "w") as file:
        file.write(str(new_chat_id))
    print(f"Chat ID updated to: {new_chat_id}")


@receiver(post_save, sender=TelemetryModel)
def send_tele_group_notification(sender, instance, created, **kwargs):
    """
    Build and send a detailed telemetry update via Telegram Bot
    whenever new telemetry is created.
    """
    # Only act on new records
    if not created:
        return

    # Format timestamp for human-readable output
    formatted_ts = instance.timestamp.strftime("%b %d, %Y, %H:%M")

    # Construct Markdown-formatted message body
    message = (
        f"📡 *Telemetry Update*\n\n"
        f"*Satellite:* {instance.satellite.name}\n"
        f"*Timestamp:* {formatted_ts}\n\n"
        f"*Position:*\n"
        f"- Lat: `{instance.latitude}°`\n"
        f"- Lon: `{instance.longitude}°`\n"
        f"- Alt: `{round(instance.altitude, 2)} km`\n\n"
        f"*Velocity:* `{round(instance.velocity, 2)} km/s`\n\n"
        f"*Health Status:* {instance.health_status}\n\n"
        f"*Battery Voltage:* `{round(instance.battery_voltage, 1)} V`\n\n"
        f"*Solar Panel Status:* {instance.solar_panel_status}\n\n"
        f"*Temperature:* `{round(instance.temperature, 1)}°C`\n\n"
        f"*Signal Strength:* `{round(instance.signal_strength, 2)} dBm`\n\n"
        f"*Attitude:*\n"
        f"- Pitch: `{round(instance.pitch, 1)}°`\n"
        f"- Yaw: `{round(instance.yaw, 1)}°`\n"
        f"- Roll: `{round(instance.roll, 1)}°`\n\n"
        f"*Power Consumption:* `{round(instance.power_consumption, 2)} W`\n"
        f"*Data Rate:* `{round(instance.data_rate, 2)} Mbps`\n"
        f"*Command Status:* {instance.command_status}"
    )

    # Retrieve stored chat ID for Telegram
    chat_id = get_chat_id()
    if not chat_id:
        print(
            "Chat ID not found. Ensure CHAT_ID_FILE_PATH contains a valid ID."
        )
        return

    # Send the message using Telegram Bot API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    resp = requests.post(url, json=payload)

    # Handle possible migration error for Telegram group IDs
    if resp.status_code == 200:
        print("Telemetry message sent successfully!")
    elif resp.status_code == 400:
        data = resp.json()
        # Telegram may instruct to migrate chat ID (e.g. group -> supergroup)
        migrate = data.get("parameters", {}).get("migrate_to_chat_id")
        if migrate:
            update_chat_id(migrate)
            # Retry with updated ID
            payload["chat_id"] = migrate
            retry = requests.post(url, json=payload)
            if retry.status_code == 200:
                print("Sent successfully after updating chat ID.")
            else:
                print("Failed even after chat ID migration.", retry.json())
        else:
            print("Bad Request from Telegram API:", data)
    else:
        print(
            f"Telegram API error {resp.status_code}: {resp.json()}"
        )

