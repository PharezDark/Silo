from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # Each user opens a dedicated socket connection using their account ID
    path('ws/timeline/', consumers.TimelineConsumer.as_asgi()),
]