import os
from datetime import timedelta
from django.utils import timezone
from django.db import models
from skyfield.api import load
from main.entities.tle import SatelliteTLE

max_days = 3.0

def downloaded_satellites_tle():
    try:
        # Check for satellites needing an update (older than max_days) or with empty TLE lines
        stale_satellites = SatelliteTLE.objects.filter(
            models.Q(last_updated__lt=timezone.now() - timedelta(days=max_days)) |
            models.Q(line1='') | models.Q(line2='')
        )

        if not stale_satellites.exists():
            print("TLE data is up to date.")
            return

        for satellite in stale_satellites:
            # Use the satellite's method to get the appropriate TLE URL
            url = satellite.get_tle_update_url()

            # Define the file path to save the downloaded TLE data
            group_file_path = f'./repo/{satellite.tle_group}_tle.txt'  # Adjust path as needed

            # Ensure the directory for TLE files exists
            tle_directory = os.path.dirname(group_file_path)
            if not os.path.exists(tle_directory):
                os.makedirs(tle_directory)

            # Download TLE data for this satellite's group
            load.download(url, filename=group_file_path)

            with open(group_file_path, 'r') as f:
                lines = f.readlines()

            # Parse the TLE data for each satellite in the file
            tle_sets = [lines[i:i + 3] for i in range(0, len(lines), 3)]

            # Check if the TLE data contains the matching name and update
            for tle_set in tle_sets:
                name = tle_set[0].strip()
                if name == satellite.name:
                    line1 = tle_set[1].strip()
                    line2 = tle_set[2].strip()
                    # Update satellite record
                    SatelliteTLE.objects.filter(id=satellite.id).update(
                        line1=line1,
                        line2=line2,
                        last_updated=timezone.now()
                    )
                    print(f"Updated TLE for {name}")
                    break
            else:
                print(f"No matching TLE found in group {satellite.tle_group} for {satellite.name}")

    except Exception as e:
        print(f"Error in downloaded_satellites_tle: {e}")
