from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_telemetry_update(telemetry_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "telemetry_group",
        {
            "type": "telemetry_notification",
            "data": telemetry_data,
        },
    )
