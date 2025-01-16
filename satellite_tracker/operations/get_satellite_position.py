import time

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from skyfield.api import wgs84, load, EarthSatellite

from main.entities.ground_station import GroundStation
from main.entities.tle import SatelliteTLE
from .values import latitude, longitude, satellites_names


@database_sync_to_async
def get_tle_data():
    return list(SatelliteTLE.objects.filter(orbit_status='orbiting'))

@database_sync_to_async
def get_ground_station_data():
    return GroundStation.objects.all().first()

async def satellite_position():

    ts = load.timescale()
    t = ts.now()

    gs = await get_ground_station_data()

    ground_station = wgs84.latlon(gs.latitude, gs.longitude)

    # Fetch TLE data from the database
    tle_data = await get_tle_data()

    print("-----------------------------------------------------------------------")
    print("SATELLITE POSITION")

    # List to store the positions of all satellites
    satellite_positions = []

    for tle in tle_data:
        satellite = EarthSatellite(tle.line1, tle.line2, tle.name, ts)
        geocentric = satellite.at(t)

        lat, lon = wgs84.latlon_of(geocentric)

        difference = satellite - ground_station

        topo_centric = difference.at(t)
        alt, az, distance = topo_centric.altaz()

        # Create an object for the satellite's position with all the necessary details
        satellite_info = {
            "name": satellite.name,
            "elevation": round(alt.degrees, 1),
            "azimuth": round(az.degrees, 1),
            "distance_km": round(distance.km, 1),
            "latitude": lat.degrees,
            "longitude": lon.degrees
        }

        print(f"Satellite: {satellite_info['name']} ----- Elv: {satellite_info['elevation']}° Azm: {satellite_info['azimuth']}° distance: {satellite_info['distance_km']} km ===> lat: {satellite_info['latitude']} lon: {satellite_info['longitude']}")

        # Append the satellite info object to the list
        satellite_positions.append(satellite_info)

    # Sort the list by distance (closest satellite first)
    satellite_positions.sort(key=lambda x: x['distance_km'])

    return satellite_positions

