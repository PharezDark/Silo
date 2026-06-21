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
        # Convert group name string strictly to a clean alphanumeric ID format
        self.room_group_name = f"chat_{self.thread_id}"

        # Verify the logged-in user actually belongs in this private thread
        if not await self.is_thread_member():
            await self.close()
            return

        # Mark unread messages as read upon connection initialization
        await self.mark_messages_as_read()

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
        try:
            data = json.loads(text_data)
            message_text = data.get('message', '').strip()

            # Terminal Print Tracker to see if the message actually reaches the backend
            print(f"--> WS RECEIVED IN BOUND PAYLOAD: {message_text} from {self.user.username}")

            if not message_text:
                print("--> WS DROP: Message text payload evaluated as empty string.")
                return

            # 1. Block and completely finish database commitment first
            # Save to database securely using the sync-to-thread bridge
            try:
                await self.save_message(message_text)
                print("--> WS DATABASE: ChatMessage successfully recorded.")
            except Exception as db_err:
                print(f"? WS DATABASE ERROR: Failed to save record: {str(db_err)}")
                return

            # 2. Dispatch broadcast down the wire to ALL connected sessions in the room
            # Broadcast out to everyone in the room channel layer
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'sender': self.user.username
                }
            )
            print(f"--> WS GROUP BROADCAST DISPATCHED: {self.room_group_name}")

        except Exception as global_err:
            print(f"? WS GLOBAL CONSUMER CRASH / Error inside consumer receive pipeline: {str(global_err)}")

    async def chat_message(self, event):
        # 3. This function catches the group_send and shoots it down the client socket
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
            return ChatMessage.objects.create(
                thread=thread,
                sender=self.user,
                message=text
            )
        except Thread.DoesNotExist:
            return None

    # Sweep database unread records for this thread
    @database_sync_to_async
    def mark_messages_as_read(self):
        try:
            Thread.objects.get(id=self.thread_id).messages.filter(
                is_read=False
            ).exclude(sender=self.user).update(is_read=True)
        except Thread.DoesNotExist:
            pass