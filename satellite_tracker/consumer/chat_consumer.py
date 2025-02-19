import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from Web_Satellite_Tracking.settings import REDIS_CLIENT
from main.entities.chats_modal import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if not text_data:
            await self.send(text_data=json.dumps({"error": "No data provided"}))
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
            return

        command = data.get("command")
        if not command:
            await self.send(text_data=json.dumps({"error": "Command not found in the data"}))
            return

        if command == "send_message":
            await self.send_message(data)
        elif command == "typing":
            await self.typing_status(data)
        elif command == "mark_read":
            await self.mark_messages_as_read(data)

    # Send a new message
    async def send_message(self, data):
        message = data.get("message")
        sender = data.get("sender")
        receiver_id = data.get("receiver_id")
        if not message or not sender:
            await self.send(text_data=json.dumps({"error": "Message and sender are required"}))
            return

            # Save the message in the database
        new_message = await sync_to_async(ChatMessage.objects.create)(
            sender_id=sender,
            receiver_id=receiver_id,
            message=message,
            timestamp=now()
        )
        new_message = await sync_to_async(ChatMessage.objects.select_related("sender").get)(id=new_message.id)

        # Save message in Redis for caching
        try:
            message_data = {
                "message": message,
                "sender": sender,
                "timestamp": new_message.timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            }
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Error preparing message data: {str(e)}"}))
            return
        REDIS_CLIENT.lpush(f"chat_history:{self.room_name}", json.dumps(message_data))

        # Increment unread count for recipient
        try:
            REDIS_CLIENT.incr(f"unread:{receiver_id}:{self.room_name}")
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Error updating unread count: {str(e)}"}))
            return

        # Broadcast to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": new_message.message,
                "sender": str(new_message.sender.id),
                "timestamp": new_message.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )

    # Handle typing status
    async def typing_status(self, data):
        user_id = data.get("user_id")
        if not user_id:
            await self.send(text_data=json.dumps({"error": "User ID is required"}))
            return
        is_typing = data.get("typing", True)

        # Set typing status in Redis with a 10-second expiration
        key = f"typing_status:{self.room_name}:{user_id}"
        try:
            if is_typing:
                REDIS_CLIENT.setex(key, 10, "true")  # Set to automatically expire after 10 seconds
            else:
                REDIS_CLIENT.delete(key)
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Error updating typing status: {str(e)}"}))
            return
        if is_typing:
            REDIS_CLIENT.setex(key, 10, "true")  # Set to automatically expire after 10 seconds
        else:
            REDIS_CLIENT.delete(key)

        # Notify other users about typing status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_typing",
                "user_id": user_id,
                "typing": is_typing,
            }
        )

    # Handle marking messages as read
    async def mark_messages_as_read(self, data):
        user_id = data.get("user_id")
        if not user_id:
            await self.send(text_data=json.dumps({"error": "User ID is required"}))
            return

        try:
            REDIS_CLIENT.delete(f"unread:{user_id}:{self.room_name}")
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Error marking messages as read: {str(e)}"}))
            return

        # Notify that messages have been read
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "update_message_status",
                "user_id": user_id,
                "status": "read"
            }
        )

    # Deliver chat message to WebSocket clients
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "status": event.get("status", "sent")
        }))

    # Update typing status
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "typing": event["typing"]
        }))

    # Update message status (read/delivered)
    async def update_message_status(self, event):
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "status": event["status"]
        }))