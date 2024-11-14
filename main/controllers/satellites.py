from django.http import JsonResponse
from django.shortcuts import render

from main.entities.tle import SatelliteTLE


def satellites(request):
    # Fetch all SatelliteTLE objects
    sat = list(SatelliteTLE.objects.all())

    # Repeat the list until it reaches at least a length of 20, then slice to exactly 20
    multiplied_sat = (sat * ((20 // len(sat)) + 1))[:20]
    context = {'satellites':  multiplied_sat}
    return render(request, "settings/satellites.html", context)
