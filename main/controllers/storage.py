from django.shortcuts import render

from main.entities.sat_pass import SatellitePass
from main.entities.tle import SatelliteTLE


def storage(request):
    pass_data = SatellitePass.objects.all().order_by('-rise_pass_time')
    satellites = SatelliteTLE.objects.all()
    context = {
        'pass_data': pass_data,
        'satellites': satellites
    }
    return render(request, "storage/index.html", context)
