# views.py
from django.shortcuts import render, redirect
from django.contrib import messages

from main.all_forms.ground_station import GroundStationForm


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
