from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.entities.sat_pass import SatellitePass
from main.entities.telemetry import TelemetryModel
from main.entities.tle import SatelliteTLE
from main.serializers import SatellitePassSerializer, TelemetryModelSerializer
import random
from datetime import datetime, timedelta

@login_required(login_url='/login')
def storage(request):
    # Assuming SatelliteTLE model has some entries
    # satellite = SatelliteTLE.objects.last()
    #
    # if satellite:
    #     start_time = datetime.now() - timedelta(days=1)  # Start from yesterday
    #     for i in range(5):  # Generate 100 dummy telemetry entries
    #         timestamp = start_time + timedelta(minutes=i * 10)  # Increment by 10 minutes
    #         TelemetryModel.objects.create(
    #             satellite=satellite,
    #             timestamp=timestamp,
    #             latitude=random.uniform(-90, 90),  # Random latitude
    #             longitude=random.uniform(-180, 180),  # Random longitude
    #             altitude=random.uniform(400, 1200),  # Altitude in kilometers
    #             velocity=random.uniform(7, 8),  # Orbital velocity in km/s
    #             health_status=random.choice(['Nominal', 'Warning', 'Critical']),
    #             battery_voltage=random.uniform(3.5, 4.2),  # Voltage in volts
    #             solar_panel_status=random.choice([True, False]),
    #             temperature=random.uniform(-20, 60),  # Celsius
    #             signal_strength=random.uniform(-120, -60),  # dBm
    #             pitch=random.uniform(-180, 180),  # Degrees
    #             yaw=random.uniform(-180, 180),  # Degrees
    #             roll=random.uniform(-180, 180),  # Degrees
    #             power_consumption=random.uniform(50, 200),  # Watts
    #             data_rate=random.uniform(0.1, 5.0),  # Mbps
    #             error_code=random.choice([None, "E101", "E102", "E200"]),
    #             command_status=random.choice(['Idle', 'Executing', 'Completed', 'Failed']),
    #             additional_data={"dummy_key": "dummy_value"}  # Example JSON field
    #         )
    #     print("Dummy telemetry data generated.")
    # else:
    #     print("No satellites found in SatelliteTLE table.")
    #


    satellite_name = request.GET.get('satellite_name')
    print(satellite_name)
    if satellite_name:
        telemetry_data = TelemetryModel.objects.filter(satellite__name=satellite_name).order_by('-timestamp')
        pass_data = SatellitePass.objects.filter(satellite_name=satellite_name).order_by('-rise_pass_time')
    else:
        telemetry_data = TelemetryModel.objects.all().order_by('-timestamp')
        pass_data = SatellitePass.objects.all().order_by('-rise_pass_time')

        # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pass_data_list = list(pass_data.values(
            'id', 'satellite_name', 'rise_pass_time', 'set_pass_time',
            'max_elevation', 'azimuth', 'distance'
        ))
        telemetry_data_list = TelemetryModelSerializer(telemetry_data, many=True)
        return JsonResponse({'pass_data': pass_data_list, 'telemetry_data': telemetry_data_list.data})

    satellites = SatelliteTLE.objects.all()
    context = {
        'pass_data': pass_data,
        'telemetry_data': telemetry_data,
        'satellites': satellites
    }
    return render(request, "storage/index.html", context)


class SatellitePassListView(APIView):
    def get(self, request):
        satellite_passes = SatellitePass.objects.order_by('-set_pass_time')[:20]
        serializer = SatellitePassSerializer(satellite_passes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

