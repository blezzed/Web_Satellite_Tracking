# views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from main.all_forms.ground_station import GroundStationForm
from main.entities.ground_station import GroundStation


def add_ground_station(request):
    if request.method == 'POST':
        form = GroundStationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ground station added successfully!")
            return redirect('index')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GroundStationForm()
    return render(request, 'home/index.html', {'form': form})


def edit_ground_station(request, pk):
    ground_station = get_object_or_404(GroundStation, pk=pk)
    if request.method == "POST":
        form = GroundStationForm(request.POST, instance=ground_station)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
                return JsonResponse({
                    'success': True,
                    'ground_station': {
                        'name': ground_station.name,
                        'latitude': ground_station.latitude,
                        'longitude': ground_station.longitude,
                        'altitude': ground_station.altitude,
                        'start_tracking_elevation': ground_station.start_tracking_elevation
                    }
                })
            # Redirect or respond with regular success message if not an AJAX request
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = GroundStationForm(instance=ground_station)

    return render(request, "settings/ground_station.html", {"form": form, "ground_station": ground_station})