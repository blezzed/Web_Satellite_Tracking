from channels.db import database_sync_to_async
from skyfield.api import wgs84, load, EarthSatellite
from datetime import datetime, timedelta
from django.db import IntegrityError
from main.entities.sat_pass import SatellitePass
from main.entities.tle import SatelliteTLE
from .values import latitude, longitude, satellites_names, max_elevation
import pytz

@database_sync_to_async
def save_satellite_pass(satellite_name, event_time, alt_degrees, az_degrees, distance_km):
    try:
        # Attempt to save the pass, avoid duplicates
        SatellitePass.objects.get_or_create(
            satellite_name=satellite_name,
            pass_time=event_time,
            defaults={
                'max_elevation': alt_degrees,
                'azimuth': az_degrees,
                'distance': distance_km
            }
        )
        print(f"Saved new satellite pass: {satellite_name} at {event_time}")
    except IntegrityError:
        print(f"Duplicate pass for {satellite_name} at {event_time} already exists")

@database_sync_to_async
def get_tle_data():
    # Fetch all TLE data from the database
    return list(SatelliteTLE.objects.all())

async def get_satellite_passes():
    # Get the current time (Africa/Maputo timezone)
    now = datetime.now(pytz.timezone('Africa/Maputo'))

    # Load Skyfield timescale
    ts = load.timescale()

    start_time = ts.from_datetime(now)
    end_time = ts.from_datetime(now + timedelta(days=3))  # Look for passes for the next 3 days

    ground_station = wgs84.latlon(latitude, longitude)

    # Fetch TLE data from the database
    tle_data = await get_tle_data()

    all_satellite_passes = {}

    for tle in tle_data:
        satellite = EarthSatellite(tle.line1, tle.line2, tle.name, ts)
        t, events = satellite.find_events(ground_station, start_time, end_time, altitude_degrees=max_elevation)

        print(f"Processing satellite: {satellite.name}")

        passes_list = []

        event_names = 'rise above 10°', 'culminate', 'set below 10°'
        for ti, event in zip(t, events):
            name = event_names[event]

            event_time = ti.utc_datetime()
            event_time = event_time.replace(tzinfo=pytz.utc) + timedelta(hours=2)  # Adjusting to local timezone

            # Calculate elevation, azimuth, and distance
            topo_centric = (satellite - ground_station).at(ti)
            alt, az, distance = topo_centric.altaz()

            current_time = now.astimezone(pytz.utc)

            # Save pass if it occurs within the next 10 minutes
            if 0 < (event_time - current_time).total_seconds() <= 600:
                await save_satellite_pass(
                    satellite_name=satellite.name,
                    event_time=event_time,
                    alt_degrees=alt.degrees,
                    az_degrees=az.degrees,
                    distance_km=distance.km
                )

            # Add pass info to the list for return
            passes_list.append({
                'event_time': event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'event': name,
                'elevation': round(alt.degrees, 1),
                'azimuth': round(az.degrees, 1),
                'distance': round(distance.km, 1)
            })

        all_satellite_passes[satellite.name] = passes_list

    return all_satellite_passes
