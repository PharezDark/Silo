from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Matches ws/chat/<thread_id>/ urls cleanly
    re_path(r'ws/chat/(?P<thread_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]