from django.urls import path
from . import views

urlpatterns = [
    path('accept-follow/<int:notification_id>/', views.accept_follow_request, name='accept-follow'),
    path('reject-follow/<int:notification_id>/', views.decline_follow_request, name='reject-follow'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/count/', views.unread_notifications_count, name='notifications-count'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_as_read, name="mark-as-read"),
    path('followers/<int:user_id>/', views.user_followers, name='user-followers'),
    path('following/<int:user_id>/', views.user_following, name='user-following'),
    path('follow-requests/', views.follow_requests, name='follow-requests'),
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),
]