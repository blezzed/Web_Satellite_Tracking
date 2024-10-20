import time

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from skyfield.api import wgs84, load, EarthSatellite

from main.entities.tle import SatelliteTLE
from .values import latitude, longitude, satellites_names


def satellite_Elv_Azm(satellite):
    ts = load.timescale()
    t = ts.now()

    ground_station = wgs84.latlon(latitude, longitude)

    difference = satellite - ground_station

    topo_centric = difference.at(t)
    alt, az, distance = topo_centric.altaz()

    print(f"Elv: {round(alt.degrees, 1)}° Azm: {round(az.degrees, 1)}°")
    return alt.degrees

@database_sync_to_async
def get_tle_data():
    return list(SatelliteTLE.objects.all())

async def satellite_position():

    # tle_data = load.tle_file(satellites_names)

    ts = load.timescale()

    t = ts.now()

    ground_station = wgs84.latlon(latitude, longitude)

    # Fetch TLE data from the database
    tle_data = await get_tle_data()

    print("-----------------------------------------------------------------------")
    print("SATELLITE POSITION")
    print("-----------------------------------------------------------------------")

    for tle in tle_data:
        satellite = EarthSatellite(tle.line1, tle.line2, tle.name, ts)
        geocentric = satellite.at(t)

        lat, lon = wgs84.latlon_of(geocentric)

        difference = satellite - ground_station

        topo_centric = difference.at(t)
        alt, az, distance = topo_centric.altaz()

        if alt.degrees > 10:
            print("-----------------------------------------------------------------------")
            print(f'{satellite.name}'.upper())
            print("IS ABOVE THE HORIZON")
            print("-----------------------------------------------------------------------")

            while alt.degrees > 10:
                print(alt.degrees)
                alt.degrees = satellite_Elv_Azm(satellite)
                time.sleep(2)

        print(f"Satellite: {satellite.name} ----- Elv: {round(alt.degrees, 1)}° Azm: {round(az.degrees, 1)}° distance: {round(distance.km, 1)} km ===> lat: {lat} lon: {lon}")
    print()

