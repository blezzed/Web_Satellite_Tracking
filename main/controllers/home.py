
from django.shortcuts import render


def home(request):
    # SatelliteTLE.objects.create(name="NOAA 18")
    context = {}
    return render(request, "home/index.html", context)
