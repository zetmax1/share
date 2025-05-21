# from django.urls import path
# from . import views

# urlpatterns = [
#     path('login/', views.loginPage, name='login'),
#     path('logout/', views.logoutUser, name='logout'),
#     path('register/', views.registerUser, name='register'),
#     path('profile/<str:pk>/', views.userProfile, name='user-profile'),
#     path('', views.home, name='home'),
#     path('room/<str:pk>/', views.room, name='room'),
#     path('create-room/', views.createRoom, name='create-room'),
#     path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
#     path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
#     path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
#     path('update-user/', views.updateUser , name='update-user'),
#     path('topics/', views.topicsPage , name='topics'),
#     path('activity/', views.activityPage , name='activity'),
#     # path('chat/<str:pk>/', views.sendMessage , name='chat'),
#     path('room/<int:room_id>/like/', views.like_room, name='like-room'),
#     path('room/<int:room_id>/dislike/', views.dislike_room, name='dislike-room'),
#     path('set-language/', views.set_language, name='set_language'),
    
# ]





from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('room/<str:pk>/', views.room, name='room'),
    path('register/', views.registerUser, name='register'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('update-user/', views.updateUser, name='update-user'),
    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),
    path('room/<int:room_id>/like/', views.like_room, name='like-room'),
    # path('room/<int:room_id>/like/status/', views.like_status, name="like-status"),
    path('set_language/', views.set_language, name='set_language'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('security/', views.security, name='security'),
    path('collaboration/', views.collaboration, name='collaboration'),
    path("contact/", views.contact_view, name="contact"),
  
]
