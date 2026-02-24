import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage, ChatRoom

User = get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']


        if not self.user.is_authenticated:
            await self.close()
            return
        
        is_participant = await self.check_user_is_participant(self.room_name, self.user)
        if not is_participant:
            await self.close()
            return
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)


        await self.accept()

    async def recieve(self, text_data):
            text_data_json = json.loads(text_data)
            message_content = text_data_json('message')

            saved_message_data = await self.save_message(roo_id=self.room_name, sender=self.user, content=message_content)

            await self.channel_layer.group(
                self.room_group_name,{
                    'type': 'chat.message', # This calls the chat_message method below
                    'message': saved_message_data['content'],
                    'timestamp': saved_message_data['timestamp'],
                    'sender_id': saved_message_data['sender_id'],
                    'sender_name': saved_message_data['sender_name'],

                }
            )
        
    async def chat_message(self, event):
        """Called when the Channel Layer broadcasts a message to this group."""
        
        # Send data back to the client over the WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'timestamp': event['timestamp'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
        }))
        
    @database_sync_to_async
    def check_user_is_participant(self, room_id, user):
        """Ensures the user is either the buyer or the farmer in the room."""
        try:
            room = ChatRoom.objects.get(pk=room_id)
            return room.buyer == user or room.farmer == user
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room_id, sender, content):
        """Saves the message to the database and returns relevant data."""
        try:
            room = ChatRoom.objects.get(pk=room_id)
            
            # Create the message
            message = ChatMessage.objects.create(
                room=room,
                sender=sender,
                content=content,
            )
            
            # Return data needed for broadcasting
            return {
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'sender_id': sender.id,
                'sender_name': sender.first_name # Using first name for display
            }
        except ChatRoom.DoesNotExist:
            # Should not happen if the security check passed, but handles the edge case
            return None