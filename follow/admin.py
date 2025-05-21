from django.contrib import admin
from .models import Notification, Follow, FollowRequest
# Register your models here.

admin.site.register(Notification)
admin.site.register(Follow)
admin.site.register(FollowRequest)
