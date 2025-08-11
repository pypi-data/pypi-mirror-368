from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class ChatRoom(models.Model):
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1_chats')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2_chats')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ID: {self.id} | Chat between {self.user_1.username} and {self.user_2.username}"


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"iD: {self.id} | Message from {self.sender.username} at {self.timestamp} | Chatroom ID: {self.chat_room.id}"