from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChatRoomSerializer(serializers.ModelSerializer):
    user_1, user_2 = UserSerializer(read_only=True), UserSerializer(read_only=True)
    class Meta:
        model = ChatRoom
        fields = '__all__'
        depth = 1


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        depth = 1