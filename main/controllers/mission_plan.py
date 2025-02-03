import pytz
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from skyfield import almanac

from main.entities.ground_station import GroundStation
from main.entities.tle import SatelliteTLE

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from skyfield.api import wgs84, load, EarthSatellite
from datetime import datetime, timedelta


@login_required(login_url='/login')
def mission_plan(request):
    ground_station = GroundStation.objects.all().first()

    orbiting_satellites = SatelliteTLE.objects.filter(orbit_status='orbiting')

    context = {
        "GS": ground_station,
        "orbiting_satellites": orbiting_satellites,  # Add filtered satellites to the context
    }
    return render(request, "mission_plan/index.html", context)

@csrf_exempt
def predict_passes(request):
    if request.method == "POST":
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            latitude = float(data["latitude"])
            longitude = float(data["longitude"])
            satellite_id = data["satellite_id"]
            min_elevation = float(data["min_elevation"])
            prediction_days = int(data["prediction_days"])
            sun_illumination = data["sun_illumination"]

            # Get the TLE data for the selected satellite
            satellite = SatelliteTLE.objects.get(pk=satellite_id)
            line1, line2 = satellite.line1, satellite.line2
            if not line1 or not line2:
                return JsonResponse({"error": "Satellite TLE data is invalid"}, status=400)

            # Load satellite and timescale
            ts = load.timescale()
            satellite_obj = EarthSatellite(line1, line2, satellite.name, ts)
            ground_station = wgs84.latlon(latitude, longitude)  # Ground station location
            ephemeris = load('de421.bsp')  # Load Sun position for Sun illumination
            sun = ephemeris['sun']

            # Set up time range for predictions
            now = datetime.now(pytz.utc)
            start_time = ts.from_datetime(now)
            end_time = ts.from_datetime(now + timedelta(days=prediction_days))

            # Calculate Sun's rise and set times (per day, as Sun illumination might be day-dependent)
            sun_times = []
            if sun_illumination:
                # Get sunrise and sunset times for the ground station
                times, is_rising = almanac.find_discrete(
                    start_time, end_time, almanac.sunrise_sunset(ephemeris, ground_station)
                )

                # Group sunrise-sunset pairs
                for t, rising in zip(times, is_rising):
                    event_time = t.utc_datetime().replace(tzinfo=pytz.utc)
                    sun_times.append((event_time, "rise" if rising else "set"))

            # Convert sunrise and sunset times into intervals
            sun_intervals = []
            if sun_times:
                for i in range(0, len(sun_times) - 1, 2):  # Pair each rise and set
                    if sun_times[i][1] == "rise" and sun_times[i + 1][1] == "set":
                        sun_intervals.append((sun_times[i][0], sun_times[i + 1][0]))

            # Calculate satellite pass predictions
            t, events = satellite_obj.find_events(ground_station, start_time, end_time, altitude_degrees=min_elevation)

            passes = []  # List to hold satellite pass data
            current_pass = None

            for ti, event in zip(t, events):
                # Convert event time to UTC and set timezone
                event_time = ti.utc_datetime().replace(tzinfo=pytz.utc)

                # Check Sun illumination filter
                if sun_illumination:
                    # Pass is valid only if the event time falls into one of the Sun's intervals
                    valid_sun_illumination = any(rise <= event_time <= set for rise, set in sun_intervals)
                    if not valid_sun_illumination:
                        continue  # Skip this pass

                # Compute satellite position data
                topo_centric = (satellite_obj - ground_station).at(ti)
                alt, az, distance = topo_centric.altaz()

                # Initialize a new pass object on rise event
                if event == 0:  # Satellite Rise Event
                    current_pass = {
                        "rise_time": event_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "set_time": None,
                        "max_elevation": None,
                        "max_azimuth": None,
                        "distance": None
                    }

                elif event == 1 and current_pass is not None:  # Culmination Event
                    # Update max_elevation and max_azimuth at culmination point
                    current_pass["max_elevation"] = round(alt.degrees, 1)
                    current_pass["max_azimuth"] = round(az.degrees, 1)
                    current_pass["distance"] = round(distance.km, 1)

                elif event == 2 and current_pass is not None:  # Satellite Set Event
                    # Update set_time and finalize pass
                    current_pass["set_time"] = event_time.strftime('%Y-%m-%d %H:%M:%S')
                    passes.append(current_pass)  # Add the completed pass to the list
                    current_pass = None

            return JsonResponse({"passes": passes})
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": "Could not calculate satellite passes."}, status=500)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)