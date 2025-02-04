from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, LineString
from rest_framework import serializers

from .entities.mission_plan import MissionPlan
from .entities.profile import UserProfile
from .entities.sat_pass import SatellitePass
from .entities.telemetry import TelemetryModel
from .entities.tle import SatelliteTLE
from .models import GroundStation

from djoser.serializers import UserCreateSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'phone_number',
            'address',
            'country',
            'state',
            'city',
            'postal_code',
            'profile_image',
        ]


class CustomUserSerializer(UserCreateSerializer):
    profile = UserProfileSerializer()  # Including the nested profile serializer

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


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
    satellite = SatelliteTLESerializer(read_only=True)
    satellite_id = serializers.PrimaryKeyRelatedField(
        queryset=SatelliteTLE.objects.all(), source='satellite'
    )

    class Meta:
        model = TelemetryModel
        fields = [
            'id', 'timestamp', 'latitude', 'longitude', 'altitude',
            'battery_voltage', 'command_status', 'data_rate', 'health_status',
            'satellite', 'satellite_id',
            'temperature', 'velocity', 'power_consumption', 'solar_panel_status',
            'error_code', 'yaw', 'roll', 'pitch', 'signal_strength'
        ]

class MissionPlanSerializer(serializers.ModelSerializer):
    satellite = serializers.StringRelatedField(source='orbiting_satellite')  # Displays the related name
    # Custom field to display location as latitude/longitude
    location = serializers.SerializerMethodField()
    trajectory = serializers.SerializerMethodField()  # Add trajectory as a custom field
    sun_illumination = serializers.SerializerMethodField()  # Format sun illumination properly

    class Meta:
        model = MissionPlan
        fields = [
            'id', 'satellite', 'location', 'trajectory',
            'rise_time', 'set_time', 'max_elevation', 'sun_illumination'
        ]

    def get_location(self, obj):
        """Convert PointField into (longitude, latitude) tuple."""
        if isinstance(obj.location, Point):
            return {'longitude': obj.location.x, 'latitude': obj.location.y}  # GeoJSON-like format
        return None  # For null locations

    def get_trajectory(self, obj):
        """Convert LineStringField into a list of (latitude, longitude) tuples for the frontend."""
        if isinstance(obj.trajectory, LineString):
            return [[coord[0], coord[1]] for coord in obj.trajectory.coords]  # Reverse to (lat, lon) format
        return []  # For null or empty trajectories

    def get_sun_illumination(self, obj):
        """Convert True/False sun_illumination to 'Enabled'/'Disabled'."""
        return "Enabled" if obj.sun_illumination else "Disabled"

