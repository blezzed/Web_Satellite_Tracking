from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TelemetryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join a telemetry group for broadcasting
        await self.channel_layer.group_add("telemetry_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the telemetry group
        await self.channel_layer.group_discard("telemetry_group", self.channel_name)

    async def telemetry_notification(self, event):
        # Send telemetry data to WebSocket
        await self.send(text_data=json.dumps(event["data"]))
