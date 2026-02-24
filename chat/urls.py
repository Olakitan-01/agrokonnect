from django.urls import path
from .views import ChatRoomListCreateAPIView, ChatMessageListAPIView

urlpatterns = [
    # 1. Chat Room List and Initiation (P1-T3 Start)
    # GET: List all user's chat rooms
    # POST: Initiate chat (Body: {"listing_id": 5})
    path('rooms/', ChatRoomListCreateAPIView.as_view(), name='chat-room-list-create'),
    
    # 2. Chat Message History Retrieval
    # GET: Retrieve all messages for a specific room
    path('rooms/<int:room_pk>/messages/', ChatMessageListAPIView.as_view(), name='chat-message-list'),
]