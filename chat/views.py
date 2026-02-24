from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, LastChatMessageSerializer




# Create your views here.

class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_class = [IsAuthenticated]


    def get_query(self):
        user = self.request.user
        return ChatRoom.objects.filter(Q(buyer=user) | Q(farmer=user)).order_by('-message__timestamp')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        list = serializer.validated_data['list']
        
        # Determine participants
        farmer = listing.farmer
        buyer = request.user
        
        if buyer == farmer:
            return Response({"detail": "You cannot start a chat with yourself."},
             status=status.HTTP_400_BAD_REQUEST)
        
        try:
            room = ChatRoom.object.get(
                list=list,
                buyer=buyer,
                farmer=buyer
            )
            return Response(self.get_serializer(room).data, status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            room = ChatRoom.object.create(
                list=list,
                buyer=buyer,
                farmer=buyer
            )
            return Response(self.get_serializer(room).data, status.HTTP_201_CREATED)

class ChatMessageListAPIView(generics.ListAPIView):
    serializer_class = LastChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_pk = self.kwargs['room_pk']
        user = self.request.user
        
        try:
            room = ChatRoom.objects.get(pk=room_pk)
        except ChatRoom.DoesNotExist:
            raise generics.exceptions.NotFound("Chat room not found.")

        # Security Check: Ensure the user is a participant
        if room.buyer != user and room.farmer != user:
            raise generics.exceptions.PermissionDenied("You are not a participant in this chat room.")
            
        # Action: Mark messages sent by the OTHER party as read
        # This is how the 'unread_count' is cleared when a user enters the chat window
        room.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

        # Return all messages, ordered by timestamp (oldest first due to model Meta)
        return room.messages.all()
