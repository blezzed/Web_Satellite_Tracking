from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from main.entities.ground_station import GroundStation


@login_required(login_url='/login')
def mission_plan(request):
    ground_station = GroundStation.objects.all().first()

    context = {
        "GS": ground_station
    }
    return render(request, "mission_plan/index.html", context)