import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TimelineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Reject the handshake instantly if the connection is anonymous
        if self.user.is_anonymous:
            await self.close()
            return

        # Define a unique real-time stream group name for this specific user node
        self.timeline_group = f"user_stream_{self.user.id}"

        # Join their personal distribution group
        await self.channel_layer.group_add(
            self.timeline_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Gracefully break the multiplex channel assignment on exit
        if hasattr(self, 'timeline_group'):
            await self.channel_layer.group_discard(
                self.timeline_group,
                self.channel_name
            )

    # This method triggers automatically when a broadcast event hits the Channel Layer group
    async def stream_new_post(self, event):
        # Extract payload package out of the network wrapper
        post_data = event['payload']

        # Transmit the payload straight down the open socket line to the browser
        await self.send(text_data=json.dumps({
            "type": "NEW_POST_SIGNAL",
            "html": post_data['html'],
            "category": post_data['category']
        }))