# satellite_tracker/sat_position_consumer.py
import asyncio
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from satellite_tracker.operations.get_satellite_position import satellite_position
from satellite_tracker.operations.get_tles import downloaded_satellites_tle


class SatelliteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

        # Run the synchronous function asynchronously
        await database_sync_to_async(downloaded_satellites_tle)()

        # Start sending satellite positions
        while True:
            position_data = await satellite_position()
            await self.send(text_data=json.dumps({
                'position': position_data,
            }))
            await asyncio.sleep(10)

    async def disconnect(self, close_code):
        # Close the WebSocket connection
        pass
