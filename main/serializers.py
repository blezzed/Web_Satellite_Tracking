from rest_framework import serializers

from .entities.sat_pass import SatellitePass
from .entities.telemetry import TelemetryModel
from .entities.tle import SatelliteTLE
from .models import GroundStation


class GroundStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundStation
        fields = ['id', 'name', 'latitude', 'longitude', 'altitude', 'start_tracking_elevation', 'is_active']


class SatelliteTLESerializer(serializers.ModelSerializer):
    class Meta:
        model = SatelliteTLE
        fields = [
            'id',
            'name',
            'line1',
            'line2',
            'last_updated',
            'created_at',
            'auto_tracking',
            'orbit_status',
            'tle_group'
        ]


class SatellitePassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatellitePass
        fields = [
            'id',
            'satellite_name',
            'rise_pass_time',
            'set_pass_time',
            'max_elevation',
            'azimuth',
            'distance',
            'created_at'
        ]


class TelemetryModelSerializer(serializers.ModelSerializer):
    satellite = SatelliteTLESerializer()

    class Meta:
        model = TelemetryModel
        fields = [
            'id', 'timestamp', 'latitude', 'longitude', 'altitude',
            'battery_voltage', 'command_status', 'data_rate', 'health_status',
            'satellite',
            'temperature', 'velocity', 'power_consumption', 'solar_panel_status',
            'error_code', 'yaw', 'roll', 'pitch', 'signal_strength'
        ]
