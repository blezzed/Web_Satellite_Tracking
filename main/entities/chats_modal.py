from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Has the message been read?
    is_delivered = models.BooleanField(default=False)  # Has the message been delivered?

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.message[:30]}"

    class Meta:
        db_table = "Chats"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["sender", "receiver"]),  # Optimize sender/receiver queries
            models.Index(fields=["is_read", "is_delivered"]),  # Optimize message status filters
        ]