# asgi.py
import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Set the default settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Web_Satellite_Tracking.settings')

# Ensure that Django apps are loaded
django.setup()  # This is crucial to ensure that apps are ready before importing routing

# Now that Django is set up, import routing
from satellite_tracker import routing  # Import routing after django.setup()

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # For HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # WebSocket URL routing
        )
    ),
})
