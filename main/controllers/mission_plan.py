import pytz
from django.utils.timezone import make_aware
from django.contrib.gis.geos import LineString, Point
from pytz import timezone, utc
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from skyfield import almanac

from main.entities.ground_station import GroundStation
from main.entities.mission_plan import MissionPlan
from main.entities.tle import SatelliteTLE

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from skyfield.api import wgs84, load, EarthSatellite
from datetime import datetime, timedelta

from main.serializers import MissionPlanSerializer
from rest_framework.response import Response

@login_required(login_url='/login')
def mission_plan(request):
    ground_station = GroundStation.objects.all().first()

    orbiting_satellites = SatelliteTLE.objects.filter(orbit_status='orbiting')

    context = {
        "GS": ground_station,
        "orbiting_satellites": orbiting_satellites,  # Add filtered satellites to the context
    }
    return render(request, "mission_plan/index.html", context)


class MissionPlanAPIView(APIView):
    def get(self, request):
        mission_plans = MissionPlan.objects.all()
        serializer = MissionPlanSerializer(mission_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Handles DELETE request
    def delete(self, request, mission_plan_id=None):
        if not mission_plan_id:
            return JsonResponse({"error": "Mission plan ID not provided."}, status=400)

        try:
            mission_plan = MissionPlan.objects.get(pk=mission_plan_id)
            mission_plan.delete()  # Delete the mission plan
            return JsonResponse({"success": "Mission plan deleted successfully."}, status=200)
        except MissionPlan.DoesNotExist:
            return JsonResponse({"error": "Mission plan not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# Helper function to group and fix sun times
def process_sun_times(sun_times, now):
    grouped_intervals = []

    # Group events by date
    day_times = {}
    for event_time, event_type in sun_times:
        event_date = event_time.date()
        if event_date not in day_times:
            day_times[event_date] = {"rise": None, "set": None}
        day_times[event_date][event_type] = event_time

    # Process each day to create intervals
    for date, events in day_times.items():
        rise = events.get("rise")
        set_ = events.get("set")

        # Handle cases where the current time falls between a lost rise or set
        if date == now.date():
            if not rise and set_ and now < set_:
                # Use now as a fallback rise time for today
                rise = now
            elif rise and not set_:
                # Skip: Today's set is missing; invalid interval
                continue

        # Ensure a valid rise and set interval
        if rise and set_:
            grouped_intervals.append((rise, set_))

    return grouped_intervals

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
                    event_type = "rise" if rising else "set"
                    sun_times.append((event_time, event_type))

            # Use helper to group sun times into intervals
            sun_intervals = process_sun_times(sun_times, now)

            # Calculate satellite pass predictions
            t, events = satellite_obj.find_events(ground_station, start_time, end_time, altitude_degrees=min_elevation)

            passes = []  # List to hold satellite pass data
            current_pass = None

            for ti, event in zip(t, events):
                # Convert event time to UTC and set timezone
                event_time = ti.utc_datetime().replace(tzinfo=pytz.utc) + timedelta(hours=2)

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

@csrf_exempt
def calculate_trajectory(request):
    if request.method == "POST":
        try:
            # Parse input JSON data
            data = json.loads(request.body)

            # Extract satellite ID
            satellite_id = data.get("satellite")
            if not satellite_id:
                return JsonResponse({"error": "Satellite ID is missing."}, status=400)

            # Get TLE data for satellite
            satellite = SatelliteTLE.objects.get(pk=satellite_id)
            ts = load.timescale()
            satellite_obj = EarthSatellite(satellite.line1, satellite.line2, satellite.name, ts)

            # Define local timezone (e.g., "UTC + 2")
            local_tz = timezone("Etc/GMT-2")

            # Convert rise and set times to timezone-aware datetime objects
            rise_time_naive = datetime.fromisoformat(data["riseTime"])
            set_time_naive = datetime.fromisoformat(data["setTime"])

            # Make them timezone-aware and convert to UTC
            rise_time = make_aware(rise_time_naive, local_tz).astimezone(utc)
            set_time = make_aware(set_time_naive, local_tz).astimezone(utc)

            # Calculate trajectory
            positions = []
            time_step = timedelta(seconds=30)
            current_time = rise_time

            while current_time <= set_time:
                t = ts.from_datetime(current_time)
                geocentric = satellite_obj.at(t)
                lat, lon = wgs84.latlon_of(geocentric)
                positions.append([lat.degrees, lon.degrees])
                current_time += time_step

            return JsonResponse({"trajectory": positions})

        except SatelliteTLE.DoesNotExist:
            return JsonResponse({"error": "Satellite not found."}, status=404)
        except Exception as e:
            print("Error calculating trajectory:", e)
            return JsonResponse({"error": "Could not calculate trajectory."}, status=500)
    else:
        return JsonResponse({"error": "Invalid method."}, status=405)

@csrf_exempt
def save_mission_plan(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)

            # Parse required fields
            latitude = float(data.get("latitude", 0))
            longitude = float(data.get("longitude", 0))
            selected_pass = data.get("selectedPass", {})
            trajectory_coords = data.get("trajectory", [])  # Expecting a list of [lat, lon] pairs

            print(selected_pass)

            # Validate required fields
            if not trajectory_coords or not latitude or not longitude:
                return JsonResponse({"error": "Incomplete configuration data."}, status=400)

            # Create a LineString for trajectory
            trajectory = LineString(trajectory_coords)

            # Create a Point for the central mission location (latitude, longitude)
            location = Point(longitude, latitude)  # Note: GIS Point uses (lon, lat) order

            # Extract pass details
            rise_time_naive = datetime.fromisoformat(selected_pass.get("riseTime"))
            set_time_naive = datetime.fromisoformat(selected_pass.get("setTime"))

            # Convert naive datetime to timezone-aware
            rise_time = make_aware(rise_time_naive)
            set_time = make_aware(set_time_naive)

            max_elevation = selected_pass.get("maxElevation", 0)
            if isinstance(max_elevation, str) and "°" in max_elevation:
                max_elevation = max_elevation.replace("°", "").strip()
            max_elevation = float(max_elevation)

            # Extract configuration fields
            orbiting_satellite = int(data.get("configuration", {}).get("orbitingSatellite"))
            min_elevation = data.get("configuration", {}).get("minElevation", 10)
            prediction_days = data.get("configuration", {}).get("predictionDays", 5)
            sun_illumination = data.get("configuration", {}).get("sunIllumination", False)

            # Save mission plan to the database
            mission_plan = MissionPlan.objects.create(
                location=location,  # Use PointField for the mission location
                rise_time=rise_time,
                set_time=set_time,
                max_elevation=max_elevation,
                trajectory=trajectory,  # Use LineStringField for trajectory
                orbiting_satellite=orbiting_satellite,
                min_elevation=min_elevation,
                prediction_days=prediction_days,
                sun_illumination=sun_illumination
            )

            return JsonResponse({"success": "Mission plan saved successfully.", "id": mission_plan.id})
        except Exception as e:
            print("Error saving mission plan:", e)
            return JsonResponse({"error": "Failed to save mission plan."}, status=500)
    else:
        return JsonResponse({"error": "Invalid method."}, status=405)