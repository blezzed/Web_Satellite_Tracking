from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.renderers import JSONRenderer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.entities.ground_station import GroundStation
from main.entities.mission_plan import MissionPlan
from main.entities.sat_pass import SatellitePass
from main.entities.telemetry import TelemetryModel
from main.entities.tle import SatelliteTLE
from main.serializers import SatellitePassSerializer, TelemetryModelSerializer, MissionPlanSerializer, \
    SatelliteTLESerializer
import random
from datetime import datetime, timedelta

@login_required(login_url='/login')
def storage(request):
    ground_station = GroundStation.objects.all().first()

    satellite_name = request.GET.get('satellite_name')
    print(satellite_name)
    if satellite_name:
        telemetry_data = TelemetryModel.objects.filter(satellite__name=satellite_name).order_by('-timestamp')
        pass_data = SatellitePass.objects.filter(satellite_name=satellite_name).order_by('-rise_pass_time')
        satellite = get_object_or_404(SatelliteTLE, name=satellite_name)

        # Filter MissionPlan using the satellite's id
        mission_plan_data = MissionPlan.objects.filter(orbiting_satellite=satellite.id).order_by('-created_at')
    else:
        telemetry_data = TelemetryModel.objects.all().order_by('-timestamp')
        pass_data = SatellitePass.objects.all().order_by('-rise_pass_time')
        mission_plan_data = MissionPlan.objects.all().order_by('-created_at')

    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pass_data_list = list(pass_data.values(
            'id', 'satellite_name', 'rise_pass_time', 'set_pass_time',
            'max_elevation', 'azimuth', 'distance'
        ))
        telemetry_data_list = TelemetryModelSerializer(telemetry_data, many=True)
        mission_plan_list = MissionPlanSerializer(mission_plan_data, many=True)  # Serialize MissionPlan data
        return JsonResponse({
            'pass_data': pass_data_list,
            'telemetry_data': telemetry_data_list.data,
            'mission_plan_data': mission_plan_list.data  # Include mission plan data in response
        })

    satellites = SatelliteTLE.objects.all()
    serializer = SatelliteTLESerializer(satellites, many=True)
    satellites_serialized = JSONRenderer().render(serializer.data).decode('utf-8')
    context = {
        "GS": ground_station,
        'pass_data': pass_data,
        'telemetry_data': telemetry_data,
        'mission_plan_data': mission_plan_data,  # Add this for initial rendering if necessary
        'satellites': satellites_serialized
    }
    return render(request, "storage/index.html", context)


class SatellitePassListView(APIView):
    def get(self, request):
        satellite_passes = SatellitePass.objects.order_by('-set_pass_time')[:20]
        serializer = SatellitePassSerializer(satellite_passes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

