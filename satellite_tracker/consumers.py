# satellite_tracker/consumers.py
import asyncio
import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from main.entities.tle import SatelliteTLE
from satellite_tracker.operations.get_tles import downloaded_satellites_tle
from satellite_tracker.operations.get_satellite_passes import get_satellite_passes
from satellite_tracker.operations.get_satellite_position import satellite_position

class SatelliteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

        # Run the synchronous function asynchronously
        await database_sync_to_async(downloaded_satellites_tle)()

        # Get satellite passes asynchronously
        satellite_passes_data = await get_satellite_passes()


        # Start sending satellite positions
        count = 0
        while count < 5:  # Simulate 60 cycles, update every 10 seconds
            print(count)
            position_data = await satellite_position()   # Fetch satellite position (replace this with actual logic)
            await self.send(text_data=json.dumps({
                'position': position_data,
                'satellite_passes': satellite_passes_data
            }))
            await asyncio.sleep(10)
            count += 1

    async def disconnect(self, close_code):
        # Close the WebSocket connection
        pass
