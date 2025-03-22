from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from Web_Satellite_Tracking.settings import REDIS_CLIENT  # Assumes you're using Redis for status tracking


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    # Mark the user as "online" in Redis
    REDIS_CLIENT.set(f"user_status:{user.id}", "online", ex=300)  # Online status expires after 5 minutes
    REDIS_CLIENT.set(f"user_last_seen:{user.id}", now().isoformat())  # Track last seen


@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    # Mark the user as "offline" and update last seen
    REDIS_CLIENT.set(f"user_status:{user.id}", "offline", ex=300)
    REDIS_CLIENT.set(f"user_last_seen:{user.id}", now().isoformat())