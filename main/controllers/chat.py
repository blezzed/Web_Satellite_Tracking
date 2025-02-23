import logging
from datetime import timedelta
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, localtime
from django.db.models import Q
from django.contrib.auth.models import User
import json

from main.entities.chats_modal import ChatMessage
from Web_Satellite_Tracking.settings import REDIS_CLIENT

logger = logging.getLogger(__name__)

@login_required(login_url='/login')
def chat(request):
    """
       Renders the chat page, including a list of chat rooms for the logged-in user.
       """
    user = request.user

    # Fetch chat rooms where the user is either the sender or receiver
    chat_messages = ChatMessage.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).select_related('sender', 'receiver').order_by('-timestamp')

    today_date = (now() + timedelta(hours=2)).date()
    yesterday_date = today_date - timedelta(days=1)

    chats = {}
    for msg in chat_messages:
        other_user = msg.receiver if msg.sender == user else msg.sender
        room_name = f"{min(user.id, other_user.id)}_{max(user.id, other_user.id)}"

        if other_user.username not in chats:
            adjusted_timestamp = msg.timestamp + timedelta(hours=2)

            redis_key = f"unread:{user.id}:{other_user.id}"  # Works for retrieving unread count
            unread_count = REDIS_CLIENT.get(redis_key)
            print(f"Redis Key: {redis_key}, Unread Count: {unread_count}")  # Debug unread count

            chats[other_user.username] = {
                "username": other_user.username,
                "receiver_id": other_user.id,
                "last_message": msg.message,
                "timestamp": adjusted_timestamp,
                "unread_count": int(unread_count or 0),
                "is_read": msg.is_read,
                "is_delivered": msg.is_delivered,
                "room_name": room_name,
                "is_sender": msg.sender == user
            }

    return render(request, "chat/index.html", {
        "chats": chats.values(),
        "today_date": today_date,
        "yesterday_date": yesterday_date,
    })

@login_required
def get_chat_users(request):
    """
    API for fetching all users.
    """
    users = User.objects.exclude(id=request.user.id).values("id", "username", "first_name", "last_name")
    return JsonResponse({"users": list(users)})

@login_required
def messages_view(request):
    """
    Loads chat messages between the logged-in user and the selected receiver.
    Groups messages by date (Today, Yesterday, and other days).
    Renders the messages.html template dynamically.
    """
    receiver_id = request.GET.get("receiver_id")
    if not receiver_id:
        return JsonResponse({"error": "Receiver ID is required"}, status=400)

    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Receiver not found"}, status=404)

    # Fetch messages between the logged-in user and the selected receiver
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user, receiver_id=receiver_id) |
         Q(receiver=request.user, sender_id=receiver_id))
    ).select_related('sender', 'receiver').order_by('timestamp')

    # Mark messages as delivered if they haven't been marked already
    ChatMessage.objects.filter(
        sender_id=receiver_id,
        receiver=request.user,
        is_delivered=False
    ).update(is_delivered=True)

    # Group messages by date
    grouped_messages = []
    today = now().date()
    yesterday = today - timedelta(days=1)

    for message_date, grouped_msgs in groupby(messages, key=lambda x: x.timestamp.date()):
        if message_date == today:
            group_label = "Today"
        elif message_date == yesterday:
            group_label = "Yesterday"
        else:
            group_label = message_date.strftime("%B %d")  # e.g., "July 24"

        grouped_messages.append({
            "date": group_label,
            "messages": list(grouped_msgs)
        })

    return render(request, "chat/messages.html", {
        "grouped_messages": grouped_messages,
        "receiver": receiver
    })

@login_required
@csrf_exempt
def send_message(request):
    """
    API endpoint to send a message. Saves the message to the database and updates Redis.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        sender = request.user
        receiver_id = data.get("receiver_id")
        message = data.get("message")

        if not receiver_id or not message:
            return JsonResponse({"error": "Invalid payload: receiver_id and message are required."}, status=400)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "Receiver not found."}, status=404)

        # Save the message in the database
        new_message = ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            timestamp=now()
        )

        # Increment unread count in Redis
        redis_key = f"unread:{receiver_id}:{sender.id}"
        REDIS_CLIENT.incr(redis_key)

        return JsonResponse({"success": "Message sent successfully"})


@login_required
def get_messages(request):
    """
    API to fetch chat messages between the logged-in user and another user.
    """
    receiver_id = request.GET.get("receiver_id")
    if not receiver_id:
        return JsonResponse({"error": "Receiver ID is required."}, status=400)

    messages = ChatMessage.objects.filter(
        (Q(sender=request.user, receiver_id=receiver_id) |
         Q(receiver=request.user, sender_id=receiver_id))
    ).select_related('sender', 'receiver').order_by('timestamp')

    # Clear unread count for the active chat in Redis
    redis_key = f"unread:{request.user.id}:{receiver_id}"
    REDIS_CLIENT.delete(redis_key)

    response_data = [
        {
            "message": msg.message,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "sender": msg.sender.username,
            "receiver": msg.receiver.username,
        }
        for msg in messages
    ]
    return JsonResponse({"messages": response_data})


@login_required
@csrf_exempt
def mark_messages_as_read(request):
    """
    API endpoint to mark messages as read for a specific chat.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        sender_id = data.get("sender_id")

        if not sender_id:
            return JsonResponse({"error": "Sender ID is required."}, status=400)

        # Update message statuses to read
        ChatMessage.objects.filter(
            sender_id=sender_id,
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

        # Clear unread count in Redis
        redis_key = f"unread:{request.user.id}:{sender_id}"
        REDIS_CLIENT.delete(redis_key)

        return JsonResponse({"success": "Messages marked as read"})


@login_required
def get_unread_count(request):
    """
    API endpoint to fetch the number of unread messages for the logged-in user.
    """
    user_id = request.user.id

    chat_keys = REDIS_CLIENT.keys(f"unread:{user_id}:*")
    unread_counts = {
        key.decode("utf-8").split(":")[-1]: int(REDIS_CLIENT.get(key))
        for key in chat_keys
    }

    return JsonResponse({"unread_counts": unread_counts})