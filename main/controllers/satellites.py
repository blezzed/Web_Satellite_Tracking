from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests as req

from main.entities.tle import SatelliteTLE
import logging


logger = logging.getLogger(__name__)


def satellites_view(request):
    # Fetch all SatelliteTLE objects
    sat = list(SatelliteTLE.objects.all())

    # Repeat the list until it reaches at least a length of 20, then slice to exactly 20
    multiplied_sat = (sat * ((20 // len(sat)) + 1))[:20]
    context = {
        'SatelliteTLE': SatelliteTLE,
        'satellites':  multiplied_sat}
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

def add_satellite(request):
    if request.method == 'POST':
        logger.info(f"Received data: {request.POST}")

        name = request.POST.get('satellite_name')
        line1 = request.POST.get('line1')
        line2 = request.POST.get('line2')
        tle_group = request.POST.get('tle_group')
        auto_tracking = request.POST.get('auto_tracking') == 'true'

        if not name or not line1 or not line2:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Log data before saving it
        logger.info(f"Saving Satellite: {name}, {line1}, {line2}, Group: {tle_group}, Auto Tracking: {auto_tracking}")

        SatelliteTLE.objects.create(
            name=name,
            line1=line1,
            line2=line2,
            tle_group=tle_group,
            auto_tracking=auto_tracking
        )

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

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

            return JsonResponse({'success': True})
        except SatelliteTLE.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Satellite not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

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
            return JsonResponse({'success': True})

        except SatelliteTLE.DoesNotExist:
            # If the satellite doesn't exist
            return JsonResponse({'success': False, 'error': 'Satellite not found'})

    # If the method is not POST, return an error
    return JsonResponse({'success': False, 'error': 'Invalid request'})