#!/usr/bin/env python3
"""
sat_pass_consumer.py

WebSocket consumer for streaming upcoming satellite passes,
issuing notifications, and persisting passes in the database.
Uses Django Channels for async handling and Skyfield for pass computation.
"""
import asyncio
import json
from datetime import datetime, timedelta
import pytz  # Timezone handling for Africa/Maputo

from asgiref.sync import sync_to_async  # Convert sync functions for async use
from channels.db import database_sync_to_async  # Run ORM in async context
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import IntegrityError  # Handle duplicate entries in DB
from webpush import send_group_notification  # Send push notifications to client groups

from main.entities.sat_pass import SatellitePass  # Django model for pass persistence
from satellite_tracker.operations.get_satellite_passes import get_satellite_passes  # Async pass generator
from satellite_tracker.operations.get_tles import downloaded_satellites_tle  # TLE refresher


def sort_satellite_passes(decodedData):
    """
    Flatten and sort a dict of satellite passes by event_time.

    Args:
        decodedData (dict): Keys are satellite names, values are lists of pass dicts

    Returns:
        list: Sorted list of pass dicts with 'satellite' key added.
    """
    all_passes = []
    # Flatten: add satellite name to each pass record
    for satellite, passes in decodedData.items():
        for sat_pass in passes:
            sat_pass['satellite'] = satellite
            all_passes.append(sat_pass)

    # Convert string timestamps to datetime for sorting
    for sat_pass in all_passes:
        sat_pass['event_time'] = datetime.strptime(
            sat_pass['event_time'], '%Y-%m-%d %H:%M:%S'
        )

    # Sort by event_time
    sorted_passes = sorted(all_passes, key=lambda x: x['event_time'])

    # Convert datetimes back to strings for JSON
    for sat_pass in sorted_passes:
        sat_pass['event_time'] = sat_pass['event_time'].strftime('%Y-%m-%d %H:%M:%S')

    return sorted_passes


@database_sync_to_async
def send_notification(message):
    """
    Send a web-push notification to the 'satellite_notifications' group.

    Args:
        message (str): Notification body text.
    """
    payload = {
        "head": "Apogee",
        "body": f"{message}",
        "icon": "/static/assets/icons/light_apogee.svg",
        "url": "/"
    }
    # Push notification with a TTL of 1000 seconds
    send_group_notification(
        group_name="satellite_notifications",
        payload=payload,
        ttl=1000
    )


class SatellitePassConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that streams satellite pass data,
    sends timed notifications, and persists passes.
    """

    async def connect(self):
        # Accept incoming WebSocket connection
        await self.accept()

        # Continuous loop: fetch, notify, and persist passes
        while True:
            # 1. Refresh stale TLE data in the database
            await database_sync_to_async(downloaded_satellites_tle)()

            # 2. Compute upcoming passes asynchronously
            satellite_passes_data = await get_satellite_passes()
            print('SATELLITE PASSES SUCCESSFULLY LOADED')

            # Stream full pass list to client immediately
            await self.send(text_data=json.dumps({
                'satellite_passes': sort_satellite_passes(satellite_passes_data)
            }))

            # Identify the next rise, culmination, and set events
            next_rise = None
            next_set = None
            culminate_event = None

            # Current time in UTC, offset to Maputo local (+2h)
            now = (
                datetime.now(pytz.timezone('Africa/Maputo'))
                .astimezone(pytz.utc)
                + timedelta(hours=2)
            )

            # Loop through each satellite's passes to find the earliest next rise/set
            for satellite, passes in satellite_passes_data.items():
                rise_event = None
                set_event = None

                for sat_pass in passes:
                    # Parse the event timestamp
                    event_time = datetime.strptime(
                        sat_pass['event_time'], '%Y-%m-%d %H:%M:%S'
                    ).replace(tzinfo=pytz.utc)

                    # Capture the next 'Satellite Rise'
                    if sat_pass['event'] == 'Satellite Rise' and event_time > now:
                        rise_event = {'event_time': event_time, 'pass_data': sat_pass}

                    # Capture culmination after rise
                    if rise_event and sat_pass['event'] == 'culminate' and event_time > rise_event['event_time']:
                        culminate_event = {'event_time': event_time, 'pass_data': sat_pass}

                    # Capture 'Satellite Set' for the same pass and break
                    if rise_event and sat_pass['event'] == 'Satellite Set' and event_time > rise_event['event_time']:
                        set_event = {'event_time': event_time, 'pass_data': sat_pass}
                        break

                # Compare to global next_rise and update if earlier
                if rise_event and set_event:
                    if next_rise is None or rise_event['event_time'] < next_rise['event_time']:
                        next_rise = {'satellite': satellite, **rise_event}
                        next_set = {'satellite': satellite, **set_event}

            # If no upcoming pass found, wait and retry
            if not next_rise or not next_set:
                print("No upcoming satellite passes found.")
                await asyncio.sleep(60)
                continue

            # Recompute 'now' before scheduling notifications
            now = (
                datetime.now(pytz.timezone('Africa/Maputo'))
                .astimezone(pytz.utc)
                + timedelta(hours=2)
            )

            # 3. Schedule 20-minute-before notification
            time_until_pass = (next_rise['event_time'] - now).total_seconds()
            lead_20 = time_until_pass - 20 * 60
            if lead_20 > 0:
                print(f"Sleeping {lead_20/60:.2f} min until 20m before pass of {next_rise['satellite']}.")
                await asyncio.sleep(lead_20)

                # Notify client via WebSocket
                await self.send(text_data=json.dumps({
                    'id': 1,
                    'message': f"20 minutes until pass of {next_rise['satellite']} at {next_rise['event_time']}. Max Elv: {culminate_event['pass_data']['elevation']}°",
                    'pass_data': next_rise['pass_data'],
                    'satellite_passes': sort_satellite_passes(satellite_passes_data)
                }, default=str))

                # Send web-push notification
                await send_notification(f"20 minutes until pass of {next_rise['satellite']} at {next_rise['event_time']}")

            # 4. Schedule 5-minute-before notification
            now = (
                datetime.now(pytz.timezone('Africa/Maputo'))
                .astimezone(pytz.utc)
                + timedelta(hours=2)
            )
            lead_5 = (next_rise['event_time'] - now).total_seconds() - 5 * 60
            if lead_5 > 0:
                print(f"Sleeping {lead_5/60:.2f} min until 5m before pass of {next_rise['satellite']}.")
                await asyncio.sleep(lead_5)

                await self.send(text_data=json.dumps({
                    'id': 2,
                    'message': f"5 minutes until pass of {next_rise['satellite']} at {next_rise['event_time']}. Max Elv: {culminate_event['pass_data']['elevation']}°",
                    'pass_data': next_rise['pass_data'],
                    'satellite_passes': sort_satellite_passes(satellite_passes_data)
                }, default=str))

                await send_notification(f"5 minutes until pass of {next_rise['satellite']} at {next_rise['event_time']}")

            # 5. Wait until the pass actually begins
            now = (
                datetime.now(pytz.timezone('Africa/Maputo'))
                .astimezone(pytz.utc)
                + timedelta(hours=2)
            )
            until_start = (next_rise['event_time'] - now).total_seconds()
            if until_start > 0:
                await asyncio.sleep(until_start)

            # 6. Persist the pass in the database, handling duplicates
            try:
                await database_sync_to_async(SatellitePass.objects.get_or_create)(
                    satellite_name=next_rise['satellite'],
                    rise_pass_time=next_rise['event_time'],
                    set_pass_time=next_set['event_time'],
                    defaults={
                        'max_elevation': culminate_event['pass_data']['elevation'],
                        'azimuth': culminate_event['pass_data']['azimuth'],
                        'distance': culminate_event['pass_data']['distance']
                    }
                )
                print(f"Saved pass for {next_rise['satellite']} at {next_rise['event_time']}")
            except IntegrityError:
                print(f"Duplicate pass for {next_rise['satellite']} at {next_rise['event_time']} already exists")

            # 7. Notify client and via push one minute after set event
            now = (
                datetime.now(pytz.timezone('Africa/Maputo'))
                .astimezone(pytz.utc)
                + timedelta(hours=2)
            )
            after_set = (next_set['event_time'] - now).total_seconds() + 60
            if after_set > 0:
                print(f"Sleeping {after_set/60:.2f} min until 1m after pass end.")
                await asyncio.sleep(after_set)

                await self.send(text_data=json.dumps({
                    'id': 3,
                    'message': f"{next_rise['satellite']} has passed at {next_set['event_time']}",
                    'pass_data': next_rise['pass_data'],
                    'satellite_passes': sort_satellite_passes(satellite_passes_data)
                }, default=str))

                await send_notification(f"{next_rise['satellite']} has passed at {next_set['event_time']}")

            # Short pause before looping for next pass
            await asyncio.sleep(1)

    async def disconnect(self, close_code):
        """
        Cleanup when WebSocket disconnects.
        """
        # No special teardown required
        pass
