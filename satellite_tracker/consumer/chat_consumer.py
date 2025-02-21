import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from django.utils.timezone import now, localtime
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
            await self.send_error("No data provided")
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": ""}))
            await self.send_error(f"Invalid JSON")
            return

        command = data.get("command")
        if not command:
            await self.send_error("Command not found in the data")
            return

        if command == "send_message":
            await self.send_message_to_room(data)
        elif command == "typing":
            await self.user_typing(data)
        elif command == "mark_read":
            await self.mark_messages_as_read(data)

    # Send a new message
    async def send_message_to_room(self, data):
        """
        Send message specifically to the current room and notify other rooms (if needed).
        """
        message = data.get("message")
        sender = data.get("sender")
        receiver_id = data.get("receiver_id")
        room_name = data.get("room_name")
        temp_id = data.get("temp_id")

        if not message or not sender or not room_name:
            await self.send_error(f"Message and sender are required")
            return

            # Save the message in the database


        try:
            new_message = await sync_to_async(ChatMessage.objects.create)(
                sender_id=sender,
                receiver_id=receiver_id,
                message=message, #todo add room name
                timestamp=now()
            )
            new_message = await sync_to_async(ChatMessage.objects.select_related("sender").get)(id=new_message.id)
        except Exception as e:
            await self.send_error(f"Error saving message: {e}")
            return

        local_time = localtime(new_message.timestamp)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            f"chat_{room_name}",
            {
                "type": "chat_message",
                "message_id": new_message.id,
                "temp_id": temp_id,
                "message": new_message.message,
                "sender": str(new_message.sender.id),
                "senderName": str(new_message.sender.username),
                "timestamp": local_time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )

    # Deliver chat message to WebSocket clients
    async def chat_message(self, event):
        """
        Send the message event to WebSocket clients.
        """
        message_id = event.get("message_id")  # Assume message_id is passed in the event

        if not message_id:
            await self.send_error("Message ID is required")
            return

        # Define the database update operation inside a function
        def mark_as_delivered():
            return ChatMessage.objects.filter(id=message_id).update(is_delivered=True)

        try:
            updated_count = await sync_to_async(mark_as_delivered)()
            print(f"Updated {updated_count} message(s) as delivered.")
        except Exception as e:
            await self.send_error(f"Error marking message as delivered: {str(e)}")

        # Notify client with the message
        await self.send(text_data=json.dumps({
            "message_id": event.get("message_id"),
            "temp_id": event.get("temp_id"),
            "message": event.get("message"),
            "sender": event.get("sender"),
            "senderName": event.get("senderName"),
            "timestamp": event.get("timestamp"),
        }))

    # Handle typing status
    async def typing_status(self, data):
        room_name = data.get("room_name")
        user_id = data.get("user_id")
        if not room_name or not user_id:
            await self.send_error("User ID is required or room name is required.")
            return

        is_typing = data.get("typing", True)
        key = f"typing_status:{self.room_name}:{user_id}"
        try:
            if is_typing and not REDIS_CLIENT.exists(key):  # Only notify if typing status has changed
                REDIS_CLIENT.setex(key, 10, "true")
                await self.channel_layer.group_send(
                    f"chat_{room_name}",
                    {
                        "type": "user_typing",
                        "user_id": user_id,
                        "typing": is_typing,
                    }
                )
            elif not is_typing:
                REDIS_CLIENT.delete(key)
                await self.channel_layer.group_send(
                    f"chat_{room_name}",
                    {
                        "type": "user_typing",
                        "user_id": user_id,
                        "typing": False,
                    }
                )
        except Exception as e:
            await self.send_error(f"Error updating typing status: {str(e)}")

    async def user_typing(self, event):
        """
        Update typing status in UI for the connected users.
        """
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "typing": event["typing"]
        }))

    # Handle marking messages as read
    async def mark_messages_as_read(self, data):
        user_id = data.get("user_id")
        if not user_id:
            await self.send(text_data=json.dumps({"error": "User ID is required"}))
            return

        async def update_messages():
            # Perform the update query in one go
            return ChatMessage.objects.filter(
                Q(receiver_id=user_id) & Q(is_read=False)
            ).update(is_read=True)

        try:
            # Perform the update using sync_to_async
            updated_count = await sync_to_async(update_messages)()
            print(f"Updated {updated_count} messages as read in the database.")

            REDIS_CLIENT.delete(f"unread:{user_id}:{self.room_name}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update_message_status",
                    "user_id": user_id,
                    "status": "read",
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Error marking messages as read: {str(e)}"}))
            return

    # Update message status (read/delivered)
    async def update_message_status(self, event):
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "status": event["status"]
        }))

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            "error": True,
            "message": message
        }))
