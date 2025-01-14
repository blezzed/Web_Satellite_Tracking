from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.entities.ground_station import GroundStation
from main.serializers import GroundStationSerializer

@login_required(login_url='/login')
def ground_station(request):
    ground_station = GroundStation.objects.all().first()
    print(ground_station)

    context = {
        "ground_station": ground_station
    }
    return render(request, "settings/ground_station.html", context)

class GroundStationListView(APIView):
    def get(self, request):
        stations = GroundStation.objects.filter(is_active=True)
        serializer = GroundStationSerializer(stations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
