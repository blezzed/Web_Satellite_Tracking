
"""
get_satellite_passes.py

Async module (Django Channels) to compute upcoming satellite passes
using Skyfield and database-backed TLE data, returning structured pass information.
"""
from channels.db import database_sync_to_async
from skyfield.api import wgs84, load, EarthSatellite
from datetime import datetime, timedelta
from django.db import IntegrityError

from main.entities.ground_station import GroundStation
from main.entities.sat_pass import SatellitePass
from main.entities.tle import SatelliteTLE
from .values import latitude, longitude, satellites_names, max_elevation
import pytz


@database_sync_to_async
def get_tle_data():
    """
    Synchronously fetch all orbiting SatelliteTLE records from Django ORM.
    Runs in thread pool to avoid blocking async event loop.
    """
    # Only include satellites actively orbiting
    return list(SatelliteTLE.objects.filter(orbit_status='orbiting'))


@database_sync_to_async
def get_ground_station_data():
    """
    Retrieve the primary GroundStation record.
    Returns the first configured station or None.
    """
    return GroundStation.objects.all().first()


async def get_satellite_passes():
    """
    Asynchronously compute upcoming satellite passes:
      1. Load current time in Africa/Maputo timezone.
      2. Build Skyfield time window (now → now+2 days).
      3. Load ground station coordinates and TLE set via async functions.
      4. For each satellite, find rise/culmination/set events above elevation cutoff.
      5. Format event times, elevations, azimuths, and distances.
      6. Return a dict mapping satellite names to lists of pass dicts.
    """
    # 1. Current local time for ground-station reference
    now = datetime.now(pytz.timezone('Africa/Maputo'))

    # 2. Initialize Skyfield timescale and window
    ts = load.timescale()
    start_time = ts.from_datetime(now)
    end_time = ts.from_datetime(now + timedelta(days=2))  # Next two days

    # 3. Fetch ground station and build Skyfield location
    gs = await get_ground_station_data()
    ground_station = wgs84.latlon(gs.latitude, gs.longitude)

    # 4. Fetch TLE records asynchronously
    tle_data = await get_tle_data()

    # Prepare result container
    all_satellite_passes = {}

    # 5. Loop through each SatelliteTLE record
    for tle in tle_data:
        # Create Skyfield satellite object
        satellite = EarthSatellite(tle.line1, tle.line2, tle.name, ts)
        # Find rise/culmination/set above minimum elevation
        times, events = satellite.find_events(
            ground_station,
            start_time,
            end_time,
            altitude_degrees=gs.start_tracking_elevation
        )

        print(f"Processing satellite: {satellite.name}")  # Debug log

        passes_list = []
        event_names = ('Satellite Rise', 'culminate', 'Satellite Set')

        # 6. Iterate over events and format data
        for ti, event in zip(times, events):
            name = event_names[event]

            # Convert event time to UTC datetime, then adjust for local timezone
            event_time = ti.utc_datetime().replace(tzinfo=pytz.utc) + timedelta(hours=2)

            # Compute topocentric position at event: elevation, azimuth, distance
            topo = (satellite - ground_station).at(ti)
            alt, az, dist = topo.altaz()

            # Append structured event info
            passes_list.append({
                'event_time': event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'event': name,
                'elevation': round(alt.degrees, 1),
                'azimuth': round(az.degrees, 1),
                'distance': round(dist.km, 1)
            })

        # Store this satellite's pass list
        all_satellite_passes[satellite.name] = passes_list

    # 7. Return the mapping of satellite names to pass lists
    return all_satellite_passes
