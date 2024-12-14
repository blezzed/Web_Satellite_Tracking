from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.entities.sat_pass import SatellitePass
from main.entities.tle import SatelliteTLE
from main.serializers import SatellitePassSerializer


def storage(request):
    satellite_name = request.GET.get('satellite_name')
    print(satellite_name)
    if satellite_name:
        pass_data = SatellitePass.objects.filter(satellite_name=satellite_name).order_by('-rise_pass_time')
    else:
        pass_data = SatellitePass.objects.all().order_by('-rise_pass_time')

        # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pass_data_list = list(pass_data.values(
            'id', 'satellite_name', 'rise_pass_time', 'set_pass_time',
            'max_elevation', 'azimuth', 'distance'
        ))
        return JsonResponse({'pass_data': pass_data_list})

    satellites = SatelliteTLE.objects.all()
    context = {
        'pass_data': pass_data,
        'satellites': satellites
    }
    return render(request, "storage/index.html", context)


class SatellitePassListView(APIView):
    def get(self, request):
        satellite_passes = SatellitePass.objects.order_by('-set_pass_time')[:20]
        serializer = SatellitePassSerializer(satellite_passes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

