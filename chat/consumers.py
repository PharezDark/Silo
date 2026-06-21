import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        # Guard clause: Kick out unauthenticated socket connection attempts
        if not self.user.is_authenticated:
            await self.close()
            return

        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'

        # Verify the logged-in user actually belongs in this private thread
        if not await self.is_thread_member():
            await self.close()
            return

        # Join the shared Redis channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if not message_text:
            return

        # Save the incoming chat record directly to the database
        await self.save_message(message_text)

        # Broadcast the data payload to every active socket inside the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        # Send the clean text data straight back down to the browser client layer
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def is_thread_member(self):
        try:
            thread = Thread.objects.get(id=self.thread_id)
            return self.user == thread.first_user or self.user == thread.second_user
        except Thread.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, text):
        try:
            thread = Thread.objects.get(id=self.thread_id)
            return ChatMessage.objects.create(thread=thread, sender=self.user, message=text)
        except Thread.DoesNotExist:
            return None
