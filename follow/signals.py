
# from django.db.models.signals import m2m_changed, post_save
# from django.dispatch import receiver
# from django.conf import settings
# from base.models import Room, Message, User
# from .models import Notification, FollowRequest, Follow

# # Like Notification (Many-to-Many Field change)
# @receiver(m2m_changed, sender=Room.likes.through)
# def create_like_notification(sender, instance, action, pk_set, **kwargs):
#     if action == "post_add":  # When a user likes a room
#         for user_id in pk_set:
#             user = User.objects.get(id=user_id)  # Get the user who liked
#             if user != instance.host:  # Avoid self-notification
#                 Notification.objects.create(
#                     sender=user,
#                     receiver=instance.host,
#                     notification_type='like',
#                     post=instance
#                 )

# # Comment Notification (New Message in a Room)
# @receiver(post_save, sender=Message)
# def create_message_notification(sender, instance, created, **kwargs):
#     if created:
#         room = instance.room
#         host = room.host
#         if instance.user != host:  # Avoid self-notification
#             Notification.objects.create(
#                 sender=instance.user,
#                 receiver=host,
#                 notification_type='comment',
#                 post=room,
#                 comment_text=instance.body
#             )

# # Follow Request Notification
# @receiver(post_save, sender=FollowRequest)
# def create_follow_request_notification(sender, instance, created, **kwargs):
#     """
#     Creates a 'follow_request' notification when a FollowRequest is created.
#     """
#     if created and not instance.accepted:
#         # Check if a notification already exists to avoid duplicates
#         existing_notification = Notification.objects.filter(
#             sender=instance.sender,
#             receiver=instance.receiver,
#             notification_type="follow_request",
#             follow_request=instance
#         ).exists()
#         if not existing_notification:
#             Notification.objects.create(
#                 sender=instance.sender,
#                 receiver=instance.receiver,
#                 notification_type="follow_request",
#                 follow_request=instance
#             )

# # New Follower Notification
# @receiver(post_save, sender=Follow)
# def create_new_follower_notification(sender, instance, created, **kwargs):
#     """
#     Creates a 'new_follower' notification when a Follow object is created.
#     """
#     if created:
#         # Check if a notification already exists to avoid duplicates
#         existing_notification = Notification.objects.filter(
#             sender=instance.follower,
#             receiver=instance.following,
#             notification_type="new_follower"
#         ).exists()
#         if not existing_notification:
#             Notification.objects.create(
#                 sender=instance.follower,
#                 receiver=instance.following,
#                 notification_type="new_follower"
#             )


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from base.models import Room, Message, User, Like  # Add Like to imports
from .models import Notification, FollowRequest, Follow

# Like Notification (Triggered when a Like instance is created)
@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:  # When a new Like instance is created
        user = instance.user  # The user who liked
        room = instance.room  # The room that was liked
        if user != room.host:  # Avoid self-notification
            Notification.objects.create(
                sender=user,
                receiver=room.host,
                notification_type='like',
                post=room
            )

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        host = room.host
        if instance.user != host:  # Avoid self-notification
            Notification.objects.create(
                sender=instance.user,
                receiver=host,
                notification_type='comment',
                post=room,
                comment_text=instance.body
            )

# Follow Request Notification
@receiver(post_save, sender=FollowRequest)
def create_follow_request_notification(sender, instance, created, **kwargs):
    """
    Creates a 'follow_request' notification when a FollowRequest is created.
    """
    if created and not instance.accepted:
        # Check if a notification already exists to avoid duplicates
        existing_notification = Notification.objects.filter(
            sender=instance.sender,
            receiver=instance.receiver,
            notification_type="follow_request",
            follow_request=instance
        ).exists()
        if not existing_notification:
            Notification.objects.create(
                sender=instance.sender,
                receiver=instance.receiver,
                notification_type="follow_request",
                follow_request=instance
            )

# New Follower Notification
@receiver(post_save, sender=Follow)
def create_new_follower_notification(sender, instance, created, **kwargs):
    """
    Creates a 'new_follower' notification when a Follow object is created.
    """
    if created:
        # Check if a notification already exists to avoid duplicates
        existing_notification = Notification.objects.filter(
            sender=instance.follower,
            receiver=instance.following,
            notification_type="new_follower"
        ).exists()
        if not existing_notification:
            Notification.objects.create(
                sender=instance.follower,
                receiver=instance.following,
                notification_type="new_follower"
            )