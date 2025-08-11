from rest_framework import viewsets, permissions
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
# from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User


# views.py
class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    model = serializer_class.Meta.model

    def get_queryset(self):
        return self.model.objects.filter(user_1=self.request.user) | self.model.objects.filter(user_2=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        user_id = self.request.data.get('user', None)
        user_2 = User.objects.filter(id=user_id).first()
        if not user_2:
            raise NotFound("کاربر مورد نظر با آی دی فرستاده شده یافت نشد.")
                
        chat_room = serializer.save(user_1=user, user_2=user_2)
    

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = self.serializer_class.Meta.model.objects.filter(user=profile.organization)
        chat_room_id = self.request.query_params.get('chat_room')
        if chat_room_id:
            queryset = queryset.filter(chat_room_id=chat_room_id)
        return queryset

    def perform_create(self, serializer):
        chat_room_id = self.request.data.get('chat_room')
        if not chat_room_id:
            raise ValidationError("فیلد chat_room اجباریه.")

        try:
            chat = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            raise NotFound("چت‌روم پیدا نشد.")

        message = serializer.save(sender=self.request.user, chat_room=chat)
        chat = message.chat_room
        chat.save()

