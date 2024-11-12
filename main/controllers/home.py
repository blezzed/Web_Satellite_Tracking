
from django.shortcuts import render
from django.contrib import messages

from main.entities.ground_station import GroundStation


def home(request):
    # SatelliteTLE.objects.create(name="NOAA 18")

    if GroundStation.objects.count() == 0:
        print("No ground stations found")
        GroundStation.objects.create(name="University of Zimbabwe", latitude=-17.7855, longitude=31.0521, altitude=0)
        messages.info(request, "No ground stations found. Please add one to proceed.")

    ground_station = GroundStation.objects.all().first()

    context = {
        "GS": ground_station
    }
    return render(request, "home/index.html", context)
