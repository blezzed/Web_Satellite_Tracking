
from datetime import timedelta
from django.utils import timezone
from django.db import models

from skyfield.api import load

from main.entities.tle import SatelliteTLE
from .values import weather_tle, satellites_names

base = 'https://celestrak.org/NORAD/elements/gp.php'
url = base + '?GROUP=weather&FORMAT=tle'

max_days = 7.0

def downloaded_satellites_tle():
    try:
        last_update = SatelliteTLE.objects.aggregate(models.Max('last_updated'))['last_updated__max']
        # Check if any satellite has empty line1 or line2
        empty_lines_exist = SatelliteTLE.objects.filter(models.Q(line1='') | models.Q(line2='')).exists()

        # Download TLE data if last update was more than max_days ago or if any satellite has empty TLE lines
        if empty_lines_exist or last_update is None or (timezone.now() - last_update) > timedelta(days=max_days):
            print("Downloading TLE data...")
            load.download(url, filename=weather_tle)

            with open(weather_tle, 'r') as f:
                lines = f.readlines()

            tle_sets = [lines[i:i + 3] for i in range(0, len(lines), 3)]

            existing_tle_names = SatelliteTLE.objects.values_list('name', flat=True)

            filtered_sets = [tle_set for tle_set in tle_sets if tle_set[0].strip() in existing_tle_names]

            if not filtered_sets:
                print("No matching satellites found.")
                return None

            for tle_set in filtered_sets:
                name = tle_set[0].strip()
                line1 = tle_set[1].strip()
                line2 = tle_set[2].strip()

                # Update existing records
                SatelliteTLE.objects.filter(name=name).update(
                    line1=line1,
                    line2=line2,)

            # with open(satellites_names, "w") as f:
            #     for tle_set in filtered_sets:
            #         f.write(tle_set[0])
            #         f.write(tle_set[1])
            #         f.write(tle_set[2])
            #
            # print(f"Written {len(filtered_sets)} TLE sets to {satellites_names}.")
            # return load.tle_file(satellites_names)

        else:
            print("TLE data is up to date.")

    except Exception as e:
        print(f"Error in downloaded_satellites: {e}")