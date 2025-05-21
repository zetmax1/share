from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Max
from django.forms import DateTimeField
from django.utils import timezone
import markdown
from pygments.formatters.html import HtmlFormatter
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static

PUBLIC = "public"
PRIVATE = "private"
AUTH_STATUS = (
    (PUBLIC, "Public"),  
    (PRIVATE, "Private"),  
)
IMAGE_EXTENSIONS = {'jpg', 'png', 'webp', 'jpeg', 'svg', 'gif'}
VIDEO_EXTENTIONS = {'mp4',}

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=False)
    bio = models.TextField(null=True)
    auth_status = models.CharField(max_length=64, choices=AUTH_STATUS, default=PUBLIC)  # Public or Private
    avatar = models.ImageField(null=True, upload_to='profile/', default='avatar.svg')

    def get_avatar_url(self):
        """Return the URL of the user's avatar, or a default avatar if none is set."""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        default_url = static('images/avatar.svg')
        return default_url

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def is_private(self):
        """Helper function to check if the account is private."""
        return self.auth_status == PRIVATE

    def __str__(self):
        return self.username


class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name[:55]
    

class DocumentTypes(models.TextChoices):
    IMAGE = "I", "image"
    VIDEO = "V", "video"
    PDF   = "P", "PDF"  
    FILE  = "F", "file"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='room_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')  
        ordering = ['-created']

    def __str__(self):
        return f"{self.user.username} likes {self.room.name}"


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='room/', null=True, blank=True)
    doc_type = models.CharField(choices=DocumentTypes.choices, max_length=1, default=DocumentTypes.FILE, blank=True)

    def total_likes(self):
        return self.room_likes.count()  

    @property
    def media_name(self):
        return self.media.name.rsplit('/', 1)[-1]

    def save(self, *args, **kwargs):
        if self.media:
            file_name: str = self.media.file.name
            file_extension = file_name.rsplit('.', 1)[-1].lower()
            if file_extension in IMAGE_EXTENSIONS:
                self.doc_type = DocumentTypes.IMAGE
            elif file_extension in VIDEO_EXTENTIONS:
                self.doc_type = DocumentTypes.VIDEO
            elif file_extension == 'pdf':
                self.doc_type = DocumentTypes.PDF
        super(Room, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

# class Room(models.Model):
#     host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
#     name = models.CharField(max_length=200)
#     description = models.TextField(null=True, blank= True)
#     participants = models.ManyToManyField(User, related_name='participants', blank=True)
#     updated = models.DateTimeField(auto_now= True)
#     created = models.DateTimeField(auto_now_add=True)
#     media = models.FileField(upload_to='room/', null=True, blank=True)
#     doc_type = models.CharField(choices=DocumentTypes.choices, max_length=1, default=DocumentTypes.FILE, blank=True)
#     likes = models.ManyToManyField(User, related_name='room_likes', blank=True)

#     def total_likes(self):
#         return self.likes.count()


#     @property
#     def media_name(self):
#         return self.media.name.rsplit('/', 1)[-1]

#     def save(self, *args, **kwargs):
#         if self.media:
#             file_name: str = self.media.file.name
#             file_extension = file_name.rsplit('.', 1)[-1].lower()
#             if file_extension in IMAGE_EXTENSIONS:
#                 self.doc_type = DocumentTypes.IMAGE
#             elif file_extension in VIDEO_EXTENTIONS:
#                 self.doc_type = DocumentTypes.VIDEO
#             elif file_extension == 'pdf':
#                 self.doc_type = DocumentTypes.PDF
#         super(Room, self).save(*args, **kwargs)

#     class Meta:
#         ordering = ['-updated', '-created']


#     def __str__(self):
#         return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now= True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[:50]

def get_default_receiver():
    User = get_user_model()
    try:
        return User.objects.get(email="zoxidjonqodirovyuta001@gmail.com").id  # Change to your second account's email
    except ObjectDoesNotExist:
        return None  # Handle missing user

class ContactSubmission(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_contact_submissions",  
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_contact_submissions",
        default=get_default_receiver,  # Automatically assign second account
        blank=True,
        null=True
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()  # This is just user input, not the receiver
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receiver:  
            User = get_user_model()
            try:
                self.receiver = User.objects.get(email="zoxidjonqodirovyuta001@gmail.com")  # Ensure receiver is correct
            except User.DoesNotExist:
                pass  # Handle missing user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} -> {self.receiver}"
