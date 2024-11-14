from django.http import JsonResponse
from django.shortcuts import render

from main.entities.tle import SatelliteTLE


def satellites(request):
    # Fetch all SatelliteTLE objects
    sat = list(SatelliteTLE.objects.all())

    # Repeat the list until it reaches at least a length of 20, then slice to exactly 20
    multiplied_sat = (sat * ((20 // len(sat)) + 1))[:20]
    context = {
        'SatelliteTLE': SatelliteTLE,
        'satellites':  multiplied_sat}
    return render(request, "settings/satellites.html", context)

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