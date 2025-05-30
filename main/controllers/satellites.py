from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests as req

from main.entities.tle import SatelliteTLE
import logging

from main.serializers import SatelliteTLESerializer

logger = logging.getLogger(__name__)

@login_required(login_url='/login')
def satellites_view(request):
    # Fetch all SatelliteTLE objects
    sat = list(SatelliteTLE.objects.all())

    # Repeat the list until it reaches at least a length of 20, then slice to exactly 20
    # multiplied_sat = (sat * ((20 // len(sat)) + 1))[:20]
    context = {
        'SatelliteTLE': SatelliteTLE,
        'satellites':  sat}
    return render(request, "settings/satellites.html", context)

def fetch_satellites(request):
    group = request.GET.get('group')
    if not group:
        return JsonResponse({'error': 'Group is required'}, status=400)

    url = f'https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle'

    try:
        # Use 'req' instead of 'requests'
        response = req.get(url)
        satellites = []

        if response.status_code == 200:
            tle_data = response.text.strip().splitlines()
            for i in range(0, len(tle_data), 3):
                name = tle_data[i].strip()
                line1 = tle_data[i + 1].strip()
                line2 = tle_data[i + 2].strip()
                satellites.append({'name': name, 'line1': line1, 'line2': line2})
        else:
            return JsonResponse({'error': 'Failed to fetch data from Celestrak'}, status=response.status_code)

        return JsonResponse({'satellites': satellites})

    except req.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

def fetch_satellites_from_url(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL is required'}, status=400)

    try:
        response = req.get(url)
        satellites = []

        if response.status_code == 200:
            tle_data = response.text.strip().splitlines()
            for i in range(0, len(tle_data), 3):
                name = tle_data[i].strip()
                line1 = tle_data[i + 1].strip()
                line2 = tle_data[i + 2].strip()
                satellites.append({'name': name, 'line1': line1, 'line2': line2})
        else:
            return JsonResponse({'error': 'Failed to fetch data from the provided URL'},
                                status=response.status_code)

        return JsonResponse({'satellites': satellites})

    except req.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login')
def add_satellite(request):
    if request.method == 'POST':
        name = request.POST.get('satellite_name')
        txt_link = request.POST.get('txt_link')
        line1 = request.POST.get('line1')
        line2 = request.POST.get('line2')
        tle_group = request.POST.get('tle_group')
        auto_tracking = request.POST.get('auto_tracking', 'false') == 'true'

        # Validate required fields
        if not name:
            return JsonResponse({'error': 'Satellite name is required.'}, status=400)

        # Save the satellite
        SatelliteTLE.objects.create(
            name=name,
            line1=line1,
            line2=line2,
            tle_group=tle_group or 'other',
            auto_tracking=auto_tracking,
            custom_tle_url=txt_link  # Save custom TLE URL if provided
        )
        return JsonResponse({'message': f"Satellite '{name}' added successfully!"}, status=201)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required(login_url='/login')
def update_satellite(request):
    # todo try sterilization
    if request.method == 'POST':
        satellite_id = request.POST.get('satellite_id')  # Get the ID of the satellite being updated
        name = request.POST.get('name')
        line1 = request.POST.get('line1')
        line2 = request.POST.get('line2')
        tle_group = request.POST.get('tle_group')
        orbit_status = request.POST.get('orbit_status')
        auto_tracking = request.POST.get('auto_tracking') == 'on'

        try:
            satellite = SatelliteTLE.objects.get(id=satellite_id)
            satellite.name = name
            satellite.line1 = line1
            satellite.line2 = line2
            satellite.tle_group = tle_group
            satellite.orbit_status = orbit_status
            satellite.auto_tracking = auto_tracking
            satellite.save()

            messages.success(request, f"{name} updated successfully!")
            return redirect("satellites")
        except SatelliteTLE.DoesNotExist:
            messages.error(request, f"{satellite_id} Satellite not found")
            return redirect("satellites")
    messages.error(request, f"Invalid request")
    return redirect("satellites")

@login_required(login_url='/login')
def delete_satellite(request):
    if request.method == 'POST':
        logger.info(f"Received data: {request.POST}")
        print(request.POST.get('satellite_id'))
        try:
            # Get the satellite_id from the request
            satellite_id = request.POST.get('satellite_id')

            # Delete the satellite from the database
            satellite = SatelliteTLE.objects.get(id=satellite_id)
            satellite.delete()

            # Return a success response
            messages.success(request, f"{satellite.name} deleted successfully!")
            return redirect("satellites")
        except SatelliteTLE.DoesNotExist:
            messages.error(request, f"{satellite_id} Satellite not found")
            return redirect("satellites")
    messages.error(request, f"Invalid request")
    return redirect("satellites")

class SatelliteTLEListView(APIView):
    def get(self, request):
        satellites = SatelliteTLE.objects.all()
        serializer = SatelliteTLESerializer(satellites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

