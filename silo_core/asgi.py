"""
ASGI config for silo_core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import posts.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silo_core.settings')

# Initialize the standard HTTP ASGI handler early
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Handles traditional HTTP requests
    "http": django_asgi_app,

    # Handles persistent live WebSocket connections
    "websocket": AuthMiddlewareStack(
        URLRouter(
            posts.routing.websocket_urlpatterns
        )
    ),
})
