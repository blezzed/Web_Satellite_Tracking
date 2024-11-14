import os
from datetime import timedelta
from django.utils import timezone
from django.db import models

from skyfield.api import load
from main.entities.tle import SatelliteTLE
from .values import weather_tle, satellites_names

base = 'https://celestrak.org/NORAD/elements/gp.php'
url = base + '?GROUP=weather&FORMAT=tle'
max_days = 3.0

def downloaded_satellites_tle():
    try:
        print(SatelliteTLE.objects.all())
        # Check if any satellites need updating (older than max_days) or have empty TLE lines
        stale_satellites = SatelliteTLE.objects.filter(
            models.Q(last_updated__lt=timezone.now() - timedelta(days=max_days)) |
            models.Q(line1='') | models.Q(line2='')
        )

        if stale_satellites.exists():
            print("Downloading TLE data...")

            # Ensure that the directory where the file will be saved exists
            tle_directory = os.path.dirname(weather_tle)
            if not os.path.exists(tle_directory):
                os.makedirs(tle_directory)  # Create the directory if it doesn't exist

            load.download(url, filename=weather_tle)

            with open(weather_tle, 'r') as f:
                lines = f.readlines()

            tle_sets = [lines[i:i + 3] for i in range(0, len(lines), 3)]

            # Get TLE names from the satellite database
            existing_tle_names = SatelliteTLE.objects.values_list('name', flat=True)

            # Filter TLE sets that match satellites in the database
            filtered_sets = [tle_set for tle_set in tle_sets if tle_set[0].strip() in existing_tle_names]

            if not filtered_sets:
                print("No matching satellites found.")
                return None

            for tle_set in filtered_sets:
                name = tle_set[0].strip()
                line1 = tle_set[1].strip()
                line2 = tle_set[2].strip()

                # Update satellite record if it's stale or has empty fields
                SatelliteTLE.objects.filter(name=name).update(
                    line1=line1,
                    line2=line2,
                    last_updated=timezone.now()  # Update the timestamp here
                )
                print(f"Updated TLE for {name}")

        else:
            print("TLE data is up to date.")

    except Exception as e:
        print(f"Error in downloaded_satellites: {e}")