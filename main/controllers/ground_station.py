from django.shortcuts import render

from main.entities.ground_station import GroundStation


def ground_station(request):
    ground_station = GroundStation.objects.all().first()
    print(ground_station)

    context = {
        "ground_station": ground_station
    }
    return render(request, "settings/ground_station.html", context)
