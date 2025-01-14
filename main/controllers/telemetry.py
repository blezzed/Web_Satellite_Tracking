from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from main.entities.telemetry import TelemetryModel
from main.serializers import TelemetryModelSerializer
from satellite_tracker.notifications import broadcast_telemetry_update


def telemetry(request):
    context = {}
    return render(request, "telemetry/index.html", context)

class TelemetryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        telemetry_data = TelemetryModel.objects.all()
        serializer = TelemetryModelSerializer(telemetry_data, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TelemetryModelSerializer(data=request.data)
        if serializer.is_valid():
            telemetry = serializer.save()

            # Broadcast telemetry data via WebSocket
            telemetry_data = {
                "id": telemetry.id,
                "satellite": telemetry.satellite.name,
                "timestamp": telemetry.timestamp.isoformat(),
                "latitude": telemetry.latitude,
                "longitude": telemetry.longitude,
                # Add additional fields as needed
            }
            print(telemetry)
            broadcast_telemetry_update(telemetry_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
