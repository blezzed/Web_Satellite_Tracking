import time
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from skyfield.api import wgs84, load, EarthSatellite
from skyfield.elementslib import osculating_elements_of
from datetime import timedelta

from main.entities.tle import SatelliteTLE

@database_sync_to_async
def get_tle_data():
    return list(SatelliteTLE.objects.filter(orbit_status='orbiting'))

async def satellite_orbit_path():
    ts = load.timescale()
    t_now = ts.now()

    # Fetch TLE data from the database
    tle_data = await get_tle_data()

    # List to store the predicted paths for all satellites
    satellite_paths = []

    for tle in tle_data:
        satellite = EarthSatellite(tle.line1, tle.line2, tle.name, ts)

        # Calculate the satellite's osculating elements
        elements = osculating_elements_of(satellite.at(t_now))

        # Orbital period in minutes
        orbital_period_minutes = elements.period_in_days * 1440  # Convert from days to minutes
        print(f'Orbital period: {orbital_period_minutes} minutes')

        # Set a time interval (e.g., every 1 minute) to calculate positions over one orbit
        interval_minutes = 1
        num_intervals = int(orbital_period_minutes / interval_minutes)

        # List to store positions over time for this satellite
        path_coords = []

        for i in range(num_intervals):
            # Calculate the time at each step of the orbit
            t_step = t_now + timedelta(minutes=i * interval_minutes)
            geocentric = satellite.at(t_step)

            # Get latitude and longitude of the satellite
            lat, lon = wgs84.latlon_of(geocentric)

            # Append the coordinates for this time step
            path_coords.append([lat.degrees, lon.degrees])

        # Store the satellite path for a single orbit
        satellite_paths.append({
            "name": satellite.name,
            "path": path_coords  # List of lat/lon positions
        })

    return satellite_paths


