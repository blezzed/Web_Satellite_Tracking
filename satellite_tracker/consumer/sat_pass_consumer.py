import asyncio
import json
from datetime import datetime, timedelta
import pytz
from asgiref.sync import sync_to_async

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import IntegrityError
from webpush import send_group_notification

from main.entities.sat_pass import SatellitePass
from satellite_tracker.operations.get_satellite_passes import get_satellite_passes
from satellite_tracker.operations.get_tles import downloaded_satellites_tle


def sort_satellite_passes(decodedData):
    # Step 1: Flatten the data into a single list
    all_passes = []
    for satellite, passes in decodedData.items():
        for sat_pass in passes:
            # Add the satellite name to each pass for reference
            sat_pass['satellite'] = satellite
            all_passes.append(sat_pass)

    # Step 2: Convert 'event_time' to datetime objects for sorting
    for sat_pass in all_passes:
        sat_pass['event_time'] = datetime.strptime(sat_pass['event_time'], '%Y-%m-%d %H:%M:%S')

    # Step 3: Sort the list by 'event_time'
    sorted_passes = sorted(all_passes, key=lambda x: x['event_time'])

    # Step 4: Convert 'event_time' back to string for JSON serialization
    for sat_pass in sorted_passes:
        sat_pass['event_time'] = sat_pass['event_time'].strftime('%Y-%m-%d %H:%M:%S')

    return sorted_passes


@database_sync_to_async
def send_notification(message):
    payload = {
        "head": "Apogee",
        "body": f"{message}",
        "icon": "/static/assets/icons/light_apogee.svg",
        "url": "/"
    }
    send_group_notification(group_name="satellite_notifications", payload=payload, ttl=1000)

class SatellitePassConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

        while True:
            # Step 1: Download the latest TLE data
            await database_sync_to_async(downloaded_satellites_tle)()

            # Step 2: Get satellite passes asynchronously (assuming this retrieves data for multiple satellites)
            satellite_passes_data = await get_satellite_passes()
            print(f'SATELLITE PASSES SUCCESSFULLY LOADED')

            await self.send(text_data=json.dumps({
                'satellite_passes': sort_satellite_passes(satellite_passes_data)
            }))


            # Step 3: Find the next satellite pass (next 'Satellite Rise') across all satellites
            next_rise = None
            next_set = None
            culminate_event = None
            now = datetime.now(pytz.timezone('Africa/Maputo')).astimezone(pytz.utc) + timedelta(hours=2) #+ timedelta(minutes=59)

            for satellite, passes in satellite_passes_data.items():
                rise_event = None
                set_event = None
                for sat_pass in passes:
                    event_time_str = sat_pass['event_time']
                    # Convert the string to datetime
                    event_time = datetime.strptime(event_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

                    # Find the next 'Satellite Rise' event
                    if sat_pass['event'] == 'Satellite Rise' and event_time > now:
                        rise_event = {
                            'event_time': event_time,  # Now it's a datetime object
                            'pass_data': sat_pass
                        }

                    if rise_event and sat_pass['event'] == 'culminate' and event_time > rise_event['event_time']:
                        culminate_event = {
                            'event_time': event_time,  # Now it's a datetime object
                            'pass_data': sat_pass
                        }

                    # Find the corresponding 'Satellite Set' event for the same pass
                    if rise_event and sat_pass['event'] == 'Satellite Set' and event_time > rise_event['event_time']:
                        set_event = {
                            'event_time': event_time,  # Now it's a datetime object
                            'pass_data': sat_pass
                        }
                        break

                # If we found a valid pair of rise and set events, check if this is the earliest rise event
                if rise_event and set_event:
                    rise_time = rise_event['event_time']

                    if next_rise is None or rise_time < next_rise['event_time']:
                        next_rise = {
                            'satellite': satellite,
                            'event_time': rise_time,
                            'pass_data': rise_event
                        }
                        next_set = {
                            'satellite': satellite,
                            'event_time': set_event['event_time'],
                            'pass_data': set_event
                        }

            if not next_rise or not next_set:
                print("No upcoming satellite passes found.")
                await asyncio.sleep(60)  # Wait for 1 minute before trying again
                continue

            now = datetime.now(pytz.timezone('Africa/Maputo')).astimezone(pytz.utc) + timedelta(hours=2) #+ timedelta(minutes=59)

            # Step 4: Calculate the time to sleep until 5 minutes before the satellite pass
            time_until_pass = (next_rise['event_time'] - now).total_seconds()
            time_until_wake_20 = time_until_pass - (20 * 60)  # 20 minutes before the pass

            if time_until_wake_20 > 0:
                print(
                    f"Sleeping {time_until_wake_20 / 60:.2f} minutes until 20 minutes before the pass of {next_rise['satellite']} at {next_rise['event_time']}")
                await asyncio.sleep(time_until_wake_20)

                await self.send(text_data=json.dumps({
                    'id': 1,
                    'message': f"20 minutes until the pass of {next_rise['satellite']} at {next_rise['event_time']}",
                    'pass_data': next_rise['pass_data'],
                    'satellite_passes': sort_satellite_passes(satellite_passes_data)
                }, default=str))

                await send_notification(f"Sleeping {time_until_wake_20 / 60:.2f} minutes until 20 minutes before the pass of {next_rise['satellite']} at {next_rise['event_time']}")

            time_until_pass = (next_rise['event_time'] - now).total_seconds()
            time_until_wake = time_until_pass - (5 * 60)  # 5 minutes before the pass

            if time_until_wake > 0:
                print(
                    f"Sleeping {time_until_wake / 60:.2f} minutes until 5 minutes before the pass of {next_rise['satellite']} at {next_rise['event_time']}")
                await asyncio.sleep(time_until_wake)

            # Step 5: Notify the client 5 minutes before the pass
                await self.send(text_data=json.dumps({
                    'id': 2,
                    'message': f"5 minutes until the pass of {next_rise['satellite']} at {next_rise['event_time']}",
                    'pass_data': next_rise['pass_data'],
                    'satellite_passes': sort_satellite_passes(satellite_passes_data)
                }, default=str))

                await send_notification(f"5 minutes until the pass of {next_rise['satellite']} at {next_rise['event_time']}")

            now = datetime.now(pytz.timezone('Africa/Maputo')).astimezone(pytz.utc) + timedelta(hours=2) #+ timedelta(minutes=59)
            time_until_pass = (next_rise['event_time'] - now).total_seconds()

            if time_until_pass > 0:
                await asyncio.sleep(time_until_pass)

            try:
                await database_sync_to_async(
                    SatellitePass.objects.get_or_create)(
                    satellite_name=next_rise['satellite'],
                    rise_pass_time=next_rise['event_time'],
                    set_pass_time=next_set['event_time'],
                    defaults={
                        'max_elevation': culminate_event['pass_data']['elevation'],
                        'azimuth': culminate_event['pass_data']['azimuth'],
                        'distance': culminate_event['pass_data']['distance']
                    }
                )
                print(
                    f"Saved new satellite pass: {next_rise['satellite']} at {next_rise['event_time']} - {next_set['event_time']}")
            except IntegrityError:
                print(
                    f"Duplicate pass for {next_rise['satellite']} at {next_rise['event_time']}-{next_set['event_time']} already exists")

            now = datetime.now(pytz.timezone('Africa/Maputo')).astimezone(pytz.utc) + timedelta(hours=2) #+ timedelta(minutes=59)

            # Step 6: Sleep until 1 minute after the satellite's 'Satellite Set' event
            time_until_after_set = (next_set['event_time'] - now).total_seconds() + (
                        1 * 60)  # 1 minute after the pass (+1 minute total)
            if time_until_after_set > 0:
                print(
                    f"Sleeping {time_until_after_set / 60:.2f} minutes until after the pass of {next_rise['satellite']} ends at {next_set['event_time']}")
                await asyncio.sleep(time_until_after_set)

                await self.send(text_data=json.dumps({
                    'id': 3,
                    'message': f"{next_rise['satellite']} has passed at {next_set['event_time']}",
                    'pass_data': next_rise['pass_data'],
                    'satellite_passes': sort_satellite_passes(satellite_passes_data)
                }, default=str))
                payload = {
                    "head": "Apogee",
                    "body": f"{next_rise['satellite']} has passed at {next_set['event_time']}",
                    "icon": "/static/assets/icons/dark_apogee.svg",
                    "url": "/"
                }

                await send_notification(f"{next_rise['satellite']} has passed at {next_set['event_time']}")

            print(f"1 minute has passed since the pass of {next_rise['satellite']} ended at {next_set['event_time']}")

            # Step 7: Continue the loop to find the next pass
            await asyncio.sleep(1)  # Prevent tight loops

    async def disconnect(self, close_code):
        # Close the WebSocket connection
        pass
