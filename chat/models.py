from django.db import models
from base.models import User
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)  # For images
    voice = models.FileField(upload_to='chat_voices/', blank=True, null=True)  # For voice messages
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)  # For generic files
    video = models.FileField(upload_to='chat_videos/', blank=True, null=True)  # For videos
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False, null=True) 
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"
