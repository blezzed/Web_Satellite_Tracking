from django.shortcuts import render

def ground_station(request):


    context = {}
    return render(request, "settings/ground_station.html", context)
