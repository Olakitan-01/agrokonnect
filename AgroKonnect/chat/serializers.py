from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from django.db.models import Q
from market_place.models import ProductListing
from typing import Optional


User = get_user_model()

class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'role')


class LastChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('content', 'timestamp', 'sender_id')


class ChatRoomSerializer(serializers.ModelSerializer):
    list_id = serializers.PrimaryKeyRelatedField(
        queryset = ProductListing.objects.all(),
        source = 'list',
        write_only = True,
        required = True
    )
    other_party = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('list_id', 'other_party', 'last_message', 'unread_count', 'buyer', 'farmer')
        read_only_fields = ('buyer', 'farmer')

    def get_other_party(self, obj) -> Optional[dict]:
        request_user = self.context['request'].user
        # Determine if the request user is the buyer or the farmer
        if obj.buyer == request_user:
            return ChatUserSerializer(obj.farmer).data
        elif obj.farmer == request_user:
            return ChatUserSerializer(obj.buyer).data
        return None

    # Logic to get the most recent message in the room
    def get_last_message(self, obj) -> Optional[dict]:
        last_msg = obj.messages.all().order_by('-timestamp').first()
        if last_msg:
            return LastChatMessageSerializer(last_msg).data
        return None

    # Logic to count unread messages sent by the other party
    def get_unread_count(self, obj) -> int:
        request_user = self.context['request'].user
        # Count messages that are unread AND were NOT sent by the requesting user
        return obj.messages.filter(is_read=False).exclude(sender=request_user).count()
