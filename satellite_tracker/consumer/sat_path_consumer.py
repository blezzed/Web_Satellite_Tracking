import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from satellite_tracker.operations.get_satellite_path import satellite_orbit_path


class SatellitePathConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        while True:
            # Get satellite paths for the next 24 hours
            satellite_paths = await satellite_orbit_path()

            # Send the satellite paths to the client
            await self.send(text_data=json.dumps({
                'satellite_paths': satellite_paths
            }))
            await asyncio.sleep(10)

    async def disconnect(self, close_code):
        pass