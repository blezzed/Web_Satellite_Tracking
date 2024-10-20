
from django.shortcuts import render

from main.entities.tle import SatelliteTLE


def home(request):
    # SatelliteTLE.objects.create(name="NOAA 18")
    context = {}
    return render(request, "home/index.html", context)
