
"""
get_tles.py

Module to identify stale or missing Two-Line Element (TLE) entries for SatelliteTLE
objects in Django, download updated TLEs from their source URLs (group or custom),
parse the file, and update the database records accordingly.
"""
import os  # filesystem operations for directory and file handling
from datetime import timedelta  # to compute age thresholds
from django.utils import timezone  # Django-aware current time
from django.db import models  # build complex query filters
from skyfield.api import load  # download utility from Skyfield

from main.entities.tle import SatelliteTLE  # Django model for satellite TLE data

# Maximum age in days before considering a TLE stale
max_days = 3.0

def downloaded_satellites_tle():
    """
    Finds SatelliteTLE records where TLE lines are empty or older than max_days,
    then downloads the relevant TLE group file (or custom URL), parses out the
    specific satellite's TLE, and updates the database timestamp and lines.

    No-op if all satellites are up to date.
    """
    try:
        # 1. Query for stale or missing TLEs
        stale_satellites = SatelliteTLE.objects.filter(
            models.Q(last_updated__lt=timezone.now() - timedelta(days=max_days)) |
            models.Q(line1='') |
            models.Q(line2='')
        )
        # 2. Restrict to satellites currently 'orbiting'
        stale_satellites = stale_satellites.filter(orbit_status='orbiting')

        # Early exit if no updates are needed
        if not stale_satellites.exists():
            print("TLE data is up to date.")
            return

        # 3. Process each satellite needing an update
        for satellite in stale_satellites:
            # Determine which URL to download: group file vs custom URL
            url = satellite.get_tle_update_url()

            # Build local file path for saving the downloaded TLE data
            if satellite.custom_tle_url:
                group_file_path = './repo/custom_tle.txt'
            else:
                group_file_path = f'./repo/{satellite.tle_group}_tle.txt'

            # Ensure the parent directory exists
            tle_directory = os.path.dirname(group_file_path)
            if not os.path.exists(tle_directory):
                os.makedirs(tle_directory)

            # 4. Download the remote TLE file to the specified path
            load.download(url, filename=group_file_path)

            # 5. Read all lines from the downloaded file
            with open(group_file_path, 'r') as f:
                lines = f.readlines()

            # 6. Split lines into chunks of three (name, line1, line2)
            tle_sets = [lines[i:i + 3] for i in range(0, len(lines), 3)]

            # 7. Locate the matching satellite and update its TLE
            for tle_set in tle_sets:
                name = tle_set[0].strip()
                if name == satellite.name:
                    line1 = tle_set[1].strip()
                    line2 = tle_set[2].strip()
                    SatelliteTLE.objects.filter(id=satellite.id).update(
                        line1=line1,
                        line2=line2,
                        last_updated=timezone.now()
                    )
                    print(f"Updated TLE for {name}")
                    break
            else:
                # If no matching entry found in the file
                print(f"No matching TLE found for {satellite.name}")

    except Exception as e:
        # General error handling to ensure failures are logged
        print(f"Error in downloaded_satellites_tle: {e}")
