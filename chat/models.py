from django.db import models
from django.conf import settings
from market_place.models import ProductListing

# Create your models here.

class ChatRoom(models.Model):
    list = models.ForeignKey(ProductListing, on_delete=models.SET_NULL, null=True, related_name='chat_rooms')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_chats')
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farmer_chats')


    class Meta:
        unique_together = ('list', 'buyer', 'farmer')

        def __string__(self):
            return f"Chat for List {self.list.id} between {self.buyer.email} and {self.farmer.email}"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='message')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read= models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        def __str__(self):
            return f"Message by {self.sender.email} at {self.timestamp.strftime('%H:%M')}"