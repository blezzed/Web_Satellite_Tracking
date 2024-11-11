# all_forms.py
from django import forms

from main.entities.ground_station import GroundStation


class GroundStationForm(forms.ModelForm):
    class Meta:
        model = GroundStation
        fields = ['name', 'latitude', 'longitude', 'altitude', 'start_tracking_elevation']
