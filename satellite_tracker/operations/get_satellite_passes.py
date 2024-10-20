from channels.db import database_sync_to_async
from skyfield.api import wgs84, load, EarthSatellite
from datetime import datetime, timedelta

from main.entities.tle import SatelliteTLE
from .values import latitude, longitude, satellites_names, max_elevation
import pytz

@database_sync_to_async
def get_tle_data():
    return list(SatelliteTLE.objects.all())

async def get_satellite_passes():
    # Get the current local time
    now = datetime.now(pytz.timezone('Africa/Maputo'))

    ts = load.timescale()

    start_time = ts.from_datetime(now)
    end_time = ts.from_datetime(now + timedelta(days=3))

    ground_station = wgs84.latlon(latitude, longitude)

    # Load the TLE file
    # tle_data = load.tle_file(satellites_names)
    # Fetch TLE data from the database
    tle_data = await get_tle_data()

    for tle in tle_data:
        satellite = EarthSatellite(tle.line1, tle.line2, tle.name, ts)
        t, events = satellite.find_events(ground_station, start_time, end_time, altitude_degrees=max_elevation)

        print("-----------------------------------------------------------------------")
        print(satellite.name)
        print("-----------------------------------------------------------------------")
        event_names = 'rise above 10°', 'culminate', 'set below 10°'
        for ti, event in zip(t, events):
            name = event_names[event]

            event_time = ti.utc_datetime()
            event_time = event_time + timedelta(hours=2)

            # Calculate elevation, azimuth, and distance at the event time
            topo_centric = (satellite - ground_station).at(ti)
            alt, az, distance = topo_centric.altaz()

            print(f"{event_time.strftime('%Y %b %d %H:%M:%S')}  {satellite.name}     Elv: {round(alt.degrees, 1)}° Azm: {round(az.degrees, 1)}° distance: {round(distance.km, 1)} km ----- {name}")
            if name == "set below 10°":
                print('<-------------------------------------------------------------------------------------------------------------------------------------------------->')
                print()

        print()
