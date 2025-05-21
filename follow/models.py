# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.utils.timezone import now
# from django.conf import settings
# from django.db.models import Max
# from django.forms import DateTimeField
# from django.utils import timezone
# from pygments.formatters.html import HtmlFormatter
# from base.models import Room


# PUBLIC = "public"
# PRIVATE = "private"
# AUTH_STATUS = (
#     (PUBLIC, "Public"),  
#     (PRIVATE, "Private"),  
# )

# class Follow(models.Model):
#     follower = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
#     )
#     following = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("follower", "following")  # Prevent duplicate follow entries

#     def __str__(self):
#         return f"{self.follower} follows {self.following}"


# class FollowRequest(models.Model):
#     sender = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_follow_requests"
#     )
#     receiver = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_follow_requests"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     accepted = models.BooleanField(default=False)

#     def accept(self):
#         """Accept the follow request."""
#         if not self.accepted:
#             self.accepted = True
#             self.save()

#             Follow.objects.get_or_create(follower=self.sender, following=self.receiver)

#             Notification.objects.create(
#                 sender=self.receiver,  # Receiver notifies the sender
#                 receiver=self.sender,
#                 notification_type="follow_accepted",
#                 follow_request = self
#             )

#             # Delete the follow request after acceptance
#             # self.delete()

#     def decline(self):
#         """Decline the follow request."""
#         # self.delete()
#         self.save()
#         # Send a notification for declined follow request
#         Notification.objects.create(
#             sender=self.receiver,
#             receiver=self.sender,
#             notification_type="follow_declined",
#             follow_request = self
#         )

#     def __str__(self):
#         return f"{self.sender} -> {self.receiver} ({'Accepted' if self.accepted else 'Pending'})"



# class Notification(models.Model):
#     NOTIFICATION_TYPES = (
#         ('like', 'Like'),
#         ('comment', 'Comment'),
#         ('follow_request', 'Follow Request'),
#         ('follow_accepted', 'Follow Accepted'),
#         ('follow_declined', 'Follow Declined'),
#         ('new_follower', 'New Follower'),
#     )

#     sender = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="sent_notifications",
#         null=True,
#         blank=True
#     )
#     receiver = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="notifications"
#     )
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
#     post = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
#     comment_text = models.TextField(null=True, blank=True)
#     follow_request = models.ForeignKey(FollowRequest, on_delete=models.CASCADE, null=True, blank=True)  # Added this
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def update_follow_status(self, accepted):
#         """Update follow request status based on acceptance."""
#         if self.follow_request:
#             self.follow_request.accepted = accepted
#             self.follow_request.save()

#     def __str__(self):
#         sender_email = self.sender.email if self.sender else "Unknown"
#         receiver_email = self.receiver.email if self.receiver else "Unknown"
#         return f"Notification from {sender_email} to {receiver_email} - {self.notification_type}"


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Max
from django.forms import DateTimeField
from django.utils import timezone
from pygments.formatters.html import HtmlFormatter
from base.models import Room

PUBLIC = "public"
PRIVATE = "private"
AUTH_STATUS = (
    (PUBLIC, "Public"),
    (PRIVATE, "Private"),
)

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("accepted", "Accepted")], default="pending")
    class Meta:
        unique_together = ("follower", "following")  # Prevent duplicate follow entries

    def __str__(self):
        return f"{self.follower} follows {self.following}"

class FollowRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_follow_requests"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_follow_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def accept(self):
        """Accept the follow request."""
        if not self.accepted:
            self.accepted = True
            self.status = "accepted"
            self.save()

            Follow.objects.get_or_create(follower=self.sender, following=self.receiver)

            Notification.objects.create(
                sender=self.receiver,
                receiver=self.sender,
                notification_type="follow_accepted",
                follow_request=self
            )

    def decline(self):
        """Decline the follow request."""
        self.status = "declined"
        self.accepted = False
        self.save()

        Notification.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            notification_type="follow_declined",
            follow_request=self
        )

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow_request', 'Follow Request'),
        ('follow_accepted', 'Follow Accepted'),
        ('follow_declined', 'Follow Declined'),
        ('new_follower', 'New Follower'),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    comment_text = models.TextField(null=True, blank=True)
    follow_request = models.ForeignKey(FollowRequest, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_email = self.sender.email if self.sender else "Unknown"
        receiver_email = self.receiver.email if self.receiver else "Unknown"
        return f"Notification from {sender_email} to {receiver_email} - {self.notification_type}"

    @classmethod
    def get_unread_count(cls, user):
        """Return the count of unread notifications for a given user."""
        return cls.objects.filter(receiver=user, is_read=False).count()