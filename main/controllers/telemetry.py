from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from main.entities.telemetry import TelemetryModel
from main.serializers import TelemetryModelSerializer


def telemetry(request):
    context = {}
    return render(request, "telemetry/index.html", context)

class TelemetryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        telemetry_data = TelemetryModel.objects.all()
        serializer = TelemetryModelSerializer(telemetry_data, many=True)
        return Response(serializer.data)