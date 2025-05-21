from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User,Like, get_default_receiver
from .forms import RoomForm, UserForm, MyUserCreationForm, ContactForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.translation import activate
from django.core.mail import send_mail
from django.conf import settings
import os
from follow.models import PUBLIC, Follow
from .utils import private_room_required

def loginPage(request):
    
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
    file_path = os.path.join(os.path.dirname(__file__), "info_login_users.txt")
    with open(file_path, "a") as file:
        file.write(user_agent + "\n")


    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:  
            user = User.objects.get(email= email)
        except:
            messages.error(request, "User does not exist.")
            
        user = authenticate(request, email= email, password= password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else: 
            error = {
                "error":"Username or Password does not exist"
            }
            


    context = {"page": page, }
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):

    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occuried during registration')
            messages.error(request, 'You might entered weak password')
            messages.error(request, 'Change your password and try again')
    return render(request, 'base/login_register.html', {'form': form})

# @login_required(login_url='login')
# def home(request):
#     q = request.GET.get('q') if request.GET.get('q') != None else ''
    
#     rooms = Room.objects.prefetch_related('likes').filter(
#         Q(host=request.user) |  # ✅ Ensure the user sees their own rooms
#         Q(host__auth_status=PUBLIC) |  
#         Q(host__followers__in=request.user.following.all())
#     ).filter(
#         Q(topic__name__icontains=q) |
#         Q(name__icontains=q) |
#         Q(description__icontains=q)
#     ).distinct()  

  
#     room_paginator = Paginator(rooms, 5)  
#     room_page_number = request.GET.get('page')  
#     rooms_page = room_paginator.get_page(room_page_number)  

#     room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) 

#     # Pagination for recent activities
#     activity_paginator = Paginator(room_messages, 5)  
#     activity_page_number = request.GET.get('activity_page')  
#     activities_page = activity_paginator.get_page(activity_page_number)  

#     topics = Topic.objects.all()[:5]  
#     room_count = rooms.count() 

#     context = {
#         'rooms': rooms_page, 
#         'topics': topics, 
#         'room_count': room_count, 
#         'room_messages': activities_page
#     }
#     return render(request, 'base/home.html', context)

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.prefetch_related('room_likes').filter(
        Q(host=request.user) |  # Ensure the user sees their own rooms
        Q(host__auth_status=PUBLIC) |  
        Q(host__followers__in=request.user.following.all())
    ).filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).distinct()

    # Add a 'liked_by_user' attribute to each room
    for room in rooms:
        room.liked_by_user = room.room_likes.filter(user=request.user).exists()

    room_paginator = Paginator(rooms, 10)  
    room_page_number = request.GET.get('page')  
    rooms_page = room_paginator.get_page(room_page_number)  

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) 

    # Pagination for recent activities
    activity_paginator = Paginator(room_messages, 10)  
    activity_page_number = request.GET.get('activity_page')  
    activities_page = activity_paginator.get_page(activity_page_number)  

    topics = Topic.objects.all()[:5]  
    room_count = rooms.count() 

    context = {
        'rooms': rooms_page, 
        'topics': topics, 
        'room_count': room_count, 
        'room_messages': activities_page
    }
    return render(request, 'base/home.html', context)


@login_required(login_url='login')
@private_room_required
def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user= request.user,
            room= room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk= room.id)
    

    context = {'room': room, 'room_messages': room_messages, "participants": participants}
    return render(request, 'base/room.html', context)


# end of new follow

# @login_required(login_url='login')
# def userProfile(request, pk):
#     user = get_object_or_404(User, id=pk)

#     # Check if the current user follows the profile user
#     is_following = user.followers.filter(follower=request.user).exists()
#     is_requested = user.received_follow_requests.filter(sender=request.user).exists()

#     # Count followers and following
#     followers_count = user.followers.count()
#     following_count = Follow.objects.filter(follower=user).count()

#     topics = Topic.objects.all()
#     room_name = f"chat_{min(request.user.id, user.id)}_{max(request.user.id, user.id)}"

#     # If the profile is public OR the user is a follower
#     if user.auth_status == "public" or is_following or request.user == user:
#         rooms = user.room_set.all()
#         room_messages = user.message_set.all()
#         context = {
#             'user': user,
#             'rooms': rooms,
#             'room_messages': room_messages,
#             'topics': topics,
#             'is_following': is_following,
#             'is_requested': is_requested,
#             'followers_count': followers_count,
#             'following_count': following_count,
#             'chat': {'room_name': room_name}
#         }
#     else:
#         # Private profile, and the user is NOT following
#         context = {
#             'user': user,
#             'topics': topics,
#             'is_following': is_following,
#             'is_requested': is_requested,
#             'followers_count': followers_count,
#             'following_count': following_count,
#             'chat': {'room_name': None}
#         }

#     return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def userProfile(request, pk):
    user = get_object_or_404(User, id=pk)

    is_following = user.followers.filter(follower=request.user).exists()
    is_requested = user.received_follow_requests.filter(sender=request.user).exists()

    followers_count = user.followers.count()
    following_count = user.following.count()

    topics = Topic.objects.all()
    room_name = f"chat_{min(request.user.id, user.id)}_{max(request.user.id, user.id)}"

    context = {
        'user': user,
        'topics': topics,
        'is_following': is_following,
        'is_requested': is_requested,
        'followers_count': followers_count,
        'following_count': following_count,
        'chat': {'room_name': room_name if request.user != user else None},
    }

    can_view_profile = user.auth_status == "public" or is_following or request.user == user
    if can_view_profile:
        rooms = user.room_set.all()
        room_messages = user.message_set.all()
        
        followers = user.followers.all()
        following = user.following.all()

        for follower in followers:
            follower.is_mutual = follower.follower.following.filter(following=user).exists()
            print(f"Follower {follower.follower.username}: is_mutual={follower.is_mutual}")

        for follow in following:
            follow.is_mutual = follow.following.followers.filter(follower=user).exists()
            print(f"Following {follow.following.username}: is_mutual={follow.is_mutual}")

        context.update({
            'rooms': rooms,
            'room_messages': room_messages,
            'followers': followers,
            'following': following,
        })
    else:
        context.update({
            'followers': [],
            'following': [],
        })

    return render(request, 'base/profile.html', context)

@login_required(login_url= 'login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
   
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        print(request.FILES)
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.host = request.user
            obj.topic = topic
            obj.save()
            return redirect('home')
    context = {'form': form, 'topics': topics}
    return render (request, 'base/room_form.html', context)

@login_required(login_url= 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('you are not allowed here!!!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name= topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url= 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('you are not allowed here!!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    content = {'obj':room }
    return render(request, 'base/delete.html', content)


@login_required(login_url= 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('you are not allowed here!!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    content = {'obj':message }
    return render(request, 'base/delete.html', content)


@login_required(login_url= 'login')
def updateUser(request):
    user = request.user        
    form = UserForm(instance= user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance= user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)


    return render(request, 'base/update-user.html', {'form': form,})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains= q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


# @login_required
# def like_room(request, room_id):
#     room = get_object_or_404(Room, id=room_id)
#     user = request.user

#     if user in room.likes.all():
#         room.likes.remove(user)  # Unlike
#         liked = False
#     else:
#         room.likes.add(user)  # Like
#         liked = True

#     return JsonResponse({'likes': room.likes.count(), 'liked': liked})

# @login_required
# def like_status(request, room_id):
#     room = get_object_or_404(Room, id=room_id)
#     liked = request.user in room.likes.all()
#     return JsonResponse({'liked': liked})
@login_required
def like_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = request.user

    like = Like.objects.filter(user=user, room=room).first()

    if like:
        # If the user has already liked the room, unlike it by deleting the Like instance
        like.delete()
        liked = False
    else:
        # If the user hasn't liked the room, create a new Like instance
        Like.objects.create(user=user, room=room)
        liked = True

    # Get the updated like count
    likes_count = room.room_likes.count()  # Using the related_name from the Like model

    return JsonResponse({'likes': likes_count, 'liked': liked})

@login_required
def like_status(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = request.user

    # Check if the user has liked the room
    liked = Like.objects.filter(user=user, room=room).exists()

    return JsonResponse({'liked': liked})



def set_language(request):
    if request.method == "POST":
        lang_code = request.POST.get('language', 'en')
        activate(lang_code)
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', lang_code)
        return response
    

def about(request):
    return render(request, 'base/about.html')

def privacy(request):
    return render(request, 'base/privacy.html')

def security(request):
    return render(request, 'base/security.html')

def collaboration(request):
    return render(request, 'base/collaboration.html')



def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save()

            subject = f"New Contact Form Submission from {submission.name}"
            message = f"""
            Name: {submission.name}
            Phone: {submission.phone}
            Email: {submission.email}
            Message: {submission.message}
            """
            
            # ✅ Send email to the receiver (your second account)
            recipient_email = "zoxidjonqodirovyuta001@gmail.com" # ✅ Use the receiver's email
            recipient_list = [recipient_email] if recipient_email else []
            if recipient_list:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        recipient_list,
                        fail_silently=False,
                    )
                    messages.success(request, "Your message has been sent successfully!", extra_tags='contact_success')  # ✅ Use 'contact_success'
                except Exception as e:
                    messages.error(request, "There was an issue sending your message. Please try again later.", extra_tags='contact_error')  # ✅ Use 'contact_error'
            else:
                messages.error(request, "No recipient email provided!", extra_tags='contact_error')

            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'base/contact.html', {'form': form})




