# from django.shortcuts import render, redirect
# from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from django.contrib.auth import authenticate, login, logout
# from .models import Notification, Follow, FollowRequest
# from django.core.paginator import Paginator
# from django.shortcuts import get_object_or_404, redirect
# from django.http import JsonResponse
# from django.utils.translation import activate
# from django.core.mail import send_mail
# from django.conf import settings
# import os
# from django.views.decorators.csrf import csrf_exempt
# from base.models import User, Room
# # Create your views here.


# @login_required
# def follow_user(request, user_id):
#     """Handles following a user or sending a follow request if the account is private."""
#     following = get_object_or_404(User, id=user_id)
#     follower = request.user

#     if follower == following:  # Prevent self-follow
#         return redirect("user-profile", pk=user_id)

#     # If already following, return
#     if Follow.objects.filter(follower=follower, following=following).exists():
    
#         return redirect("user-profile", pk=user_id)

#     # Handle private accounts
#     if following.auth_status == "private":
#         follow_request, created = FollowRequest.objects.get_or_create(sender=follower, receiver=following)

#     else:
#         # Directly follow public accounts
#         Follow.objects.create(follower=follower, following=following)
     

#     return redirect("user-profile", pk=user_id)


# @login_required
# def unfollow_user(request, user_id):
#     """Handles unfollowing a user."""
#     following = get_object_or_404(User, id=user_id)
#     follower = request.user

#     if Follow.objects.filter(follower=follower, following=following).exists():
#         Follow.objects.filter(follower=follower, following=following).delete()

#     elif FollowRequest.objects.filter(sender=follower, receiver=following).exists():
#         FollowRequest.objects.filter(sender=follower, receiver=following).delete()

#     return redirect("user-profile", pk=user_id)



# # end of following section

# # new follow


# @login_required
# def user_followers(request, user_id):
#     """Displays a list of followers."""
#     user = get_object_or_404(User, id=user_id)

#     # Prevent access if the account is private and the user is not following
#     if user.is_private() and not user.followers.filter(follower=request.user).exists() and user != request.user:
#         return redirect("user-profile", pk=user_id)  # Redirect instead of JSON response

#     followers = user.followers.all()
#     return render(request, "base/followers.html", {"user": user, "followers": followers})


# @login_required
# def user_following(request, user_id):
#     """Displays a list of users the person is following."""
#     user = get_object_or_404(User, id=user_id)

#     # Prevent access if the account is private and the user is not following
#     if user.is_private() and not user.followers.filter(follower=request.user).exists() and user != request.user:
#         return redirect("user-profile", pk=user_id)  # Redirect instead of JSON response

#     following = Follow.objects.filter(follower=user)
#     return render(request, "base/following.html", {"user": user, "following": following})




# @login_required
# def follow_requests(request):
#     requests = FollowRequest.objects.filter(receiver=request.user)
#     return render(request, "base/follow_requests.html", {"requests": requests})

#     # sender = request.user
#     # receiver = get_object_or_404(User, id=user_id)

#     # if sender != receiver:
#     #     follow_request, created = FollowRequest.objects.get_or_create(sender=sender, receiver=receiver)

#     #     if created:  # Only create a notification if the request is new
#     #         Notification.objects.create(
#     #             user=receiver,  # The user receiving the notification
#     #             sender=sender,  # The user who sent the request
#     #             notification_type='follow_request'
#     #         )
    
#     # return redirect('notifications')  # Change this to the actual notification view URL name


# # @login_required
# # def accept_follow_request(request, notification_id):
# #     """Handles accepting a follow request via notification."""

# #     # 1️⃣ Notification obyektini olish
# #     notification = get_object_or_404(Notification, id=notification_id)

# #     # 2️⃣ Notification orqali FollowRequest ni olish
# #     follow_request = notification.follow_request

# #     if not follow_request:
# #         print(f'bkbkjb   {follow_request}')
# #         return redirect("user-profile", request.user.id)  # Agar FollowRequest mavjud bo'lmasa, home ga qaytarish

# #     # 3️⃣ Foydalanuvchi faqat o'ziga yuborilgan so‘rovni qabul qilishi mumkin
# #     if follow_request.receiver != request.user:
# #         return redirect("home")

# #     # 4️⃣ Follow obyektini yaratish yoki mavjudini olish
# #     follow, created = Follow.objects.get_or_create(
# #         follower=follow_request.sender,
# #         following=follow_request.receiver
# #     )

# #     # 5️⃣ Agar yangi follow yaratilgan bo‘lsa, notification yangilanadi
# #     if created:
# #         notification.notification_type = 'follow_accepted'
# #         notification.save()

# #         # 6️⃣ Yangi notification yaratish
# #         Notification.objects.create(
# #             sender=follow_request.receiver,
# #             receiver=follow_request.sender,
# #             notification_type='follow_accepted'
# #         )

# #     # 7️⃣ FollowRequest ni qabul qilingan deb belgilash
# #     follow_request.accepted = True
# #     follow_request.save()
# #     print(f'111   {follow_request}')
# #     return redirect("user-profile", pk=request.user.id)

# @login_required
# def accept_follow_request(request, notification_id):
#     """Handles accepting a follow request via notification."""

#     notification = get_object_or_404(Notification, id=notification_id)
#     follow_request = notification.follow_request

#     if not follow_request:
#         return redirect("user-profile", request.user.id)

#     if follow_request.receiver != request.user:
#         return redirect("home")

#     # Create or retrieve the Follow object
#     Follow.objects.get_or_create(
#         follower=follow_request.sender,
#         following=follow_request.receiver
#     )

#     # Mark the FollowRequest as accepted
#     follow_request.accepted = True
#     follow_request.save()

#     # ✅ Ensure notification is correctly linked to the follow request
#     Notification.objects.create(
#         sender=follow_request.receiver,
#         receiver=follow_request.sender,
#         notification_type='follow_accepted',
#         follow_request=follow_request  # Ensure correct link!
#     )

#     return redirect("user-profile", pk=request.user.id)

# @login_required
# def decline_follow_request(request, notification_id):
#     notification = get_object_or_404(Notification, id=notification_id)
#     follow_request = notification.follow_request

#     if not follow_request:
#         return redirect("home")

#     # Foydalanuvchi faqat o'ziga yuborilgan so‘rovni rad eta oladi
#     if follow_request.receiver != request.user:
#         return redirect("user-profile", request.user.id)

#     # FollowRequest ni o'chirish
#     # follow_request.delete()

#     # Notification turini yangilash
#     notification.notification_type = 'follow_declined'
#     notification.save()

#     # Yangi notification yaratish
#     Notification.objects.create(
#         sender=follow_request.receiver,
#         receiver=follow_request.sender,
#         notification_type='follow_declined'
#     )

#     return redirect("user-profile", pk=request.user.id)

# @login_required
# def notifications_view(request):
#     """Display all notifications for the logged-in user."""
#     notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')  # Fixed `user` to `receiver`
#     return render(request, 'base/notifications.html', {'notifications': notifications})

# @login_required
# def unread_notifications_count(request):
#     """Returns the number of unread notifications for the logged-in user."""
#     count = Notification.objects.filter(receiver=request.user, is_read=False).count()  # Fixed `user` to `receiver`
#     return JsonResponse({'count': count})

# @csrf_exempt
# @login_required
# def mark_as_read(request, notification_id):
#     """Mark a single notification as read."""
#     if request.method == "POST":
#         try:
#             notification = Notification.objects.get(id=notification_id, receiver=request.user)  # Fixed `user` to `receiver`
#             notification.is_read = True
#             notification.save()
#             return JsonResponse({"success": True})
#         except Notification.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Notification not found"}, status=404)


from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Notification, Follow, FollowRequest
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils.translation import activate
from django.core.mail import send_mail
from django.conf import settings
import os
from django.views.decorators.csrf import csrf_exempt
from base.models import User, Room

@login_required
def follow_user(request, user_id):
    following = get_object_or_404(User, id=user_id)
    follower = request.user

    if follower == following:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Cannot follow yourself'}, status=400)
        return redirect("user-profile", pk=user_id)

    if Follow.objects.filter(follower=follower, following=following).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Already following'}, status=400)
        return redirect("user-profile", pk=user_id)

    if following.auth_status == "private":
        FollowRequest.objects.get_or_create(sender=follower, receiver=following)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Follow request sent'})
    else:
        Follow.objects.create(follower=follower, following=following)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Followed successfully'})

    return redirect("user-profile", pk=user_id)

@login_required
def unfollow_user(request, user_id):
    following = get_object_or_404(User, id=user_id)
    follower = request.user

    if Follow.objects.filter(follower=follower, following=following).exists():
        Follow.objects.filter(follower=follower, following=following).delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Unfollowed successfully'})
    elif FollowRequest.objects.filter(sender=follower, receiver=following).exists():
        FollowRequest.objects.filter(sender=follower, receiver=following).delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Follow request cancelled'})

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'No follow relationship or request found'}, status=400)

    return redirect("user-profile", pk=user_id)

@login_required
def user_followers(request, user_id):
    """Displays a list of followers."""
    user = get_object_or_404(User, id=user_id)

    if user.auth_status == "private" and not user.followers.filter(follower=request.user).exists() and user != request.user:
        return redirect("user-profile", pk=user_id)

    followers = user.followers.all()
    for follower in followers:
        follower.is_mutual = follower.follower.following.filter(following=user).exists()
        print(f"Follower {follower.follower.username}: is_mutual={follower.is_mutual}")

    return render(request, "base/followers.html", {"user": user, "followers": followers})

@login_required
def user_following(request, user_id):
    """Displays a list of users the person is following."""
    user = get_object_or_404(User, id=user_id)

    if user.auth_status == "private" and not user.followers.filter(follower=request.user).exists() and user != request.user:
        return redirect("user-profile", pk=user_id)

    following = Follow.objects.filter(follower=user)
    for follow in following:
        follow.is_mutual = follow.following.followers.filter(follower=user).exists()
        print(f"Following {follow.following.username}: is_mutual={follow.is_mutual}")

    return render(request, "base/following.html", {"user": user, "following": following})

@login_required
def follow_requests(request):
    """Display all follow requests for the logged-in user."""
    requests = FollowRequest.objects.filter(receiver=request.user)
    return render(request, "base/follow_requests.html", {"requests": requests})

@login_required
def accept_follow_request(request, notification_id):
    """Handles accepting a follow request via notification."""
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    follow_request = notification.follow_request

    if not follow_request or notification.notification_type != "follow_request":
        return redirect("user-profile", pk=request.user.id)

    if follow_request.receiver != request.user:
        return redirect("home")

    # Create or retrieve the Follow object
    Follow.objects.get_or_create(
        follower=follow_request.sender,
        following=follow_request.receiver
    )

    # Mark the FollowRequest as accepted
    follow_request.accepted = True
    follow_request.status = "accepted"  # Update status
    follow_request.save()

    # Update the notification status
    notification.status = "accepted"
    notification.save()

    follow = Follow.objects.filter(
        follower=follow_request.sender,
        following=follow_request.receiver
    ).first()
    if follow:
        follow.status = "accepted"
        follow.save()
    else:
        # If no Follow object exists, create one
        Follow.objects.create(
            follower=follow_request.sender,
            following=follow_request.receiver,
            status="accepted"
        )

    # Create a new notification for the sender
    Notification.objects.create(
        sender=follow_request.receiver,
        receiver=follow_request.sender,
        notification_type="follow_accepted",
        follow_request=follow_request
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"status": "accepted"})
    return redirect("user-profile", pk=request.user.id)

@login_required
def decline_follow_request(request, notification_id):
    """Handles declining a follow request via notification."""
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    follow_request = notification.follow_request

    if not follow_request or notification.notification_type != "follow_request":
        return redirect("user-profile", pk=request.user.id)

    if follow_request.receiver != request.user:
        return redirect("home")

    # Mark the FollowRequest as declined
    follow_request.accepted = False
    follow_request.status = "declined"  # Update status
    follow_request.save()

    # Update the notification status
    notification.status = "declined"
    notification.delete()

    follow = Follow.objects.filter(
        follower=follow_request.sender,
        following=follow_request.receiver
    ).first()
    if follow:
        follow.status = "declined"
        follow.save()


    # Create a new notification for the sender
    Notification.objects.create(
        sender=follow_request.receiver,
        receiver=follow_request.sender,
        notification_type="follow_declined",
        follow_request=follow_request
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"status": "declined"})
    return redirect("user-profile", pk=request.user.id)

@login_required
def notifications_view(request):
    """Display all notifications for the logged-in user."""
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    unread_count = Notification.get_unread_count(request.user)

    if request.method == "POST":
        notifications.update(is_read=True)
        return JsonResponse({"success": True})

    return render(request, 'base/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def unread_notifications_count(request):
    """Returns the number of unread notifications for the logged-in user."""
    count = Notification.get_unread_count(request.user)
    return JsonResponse({'count': count})

@csrf_exempt
@login_required
def mark_as_read(request, notification_id):
    """Mark a single notification as read."""
    if request.method == "POST":
        try:
            notification = Notification.objects.get(id=notification_id, receiver=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({"success": True})
        except Notification.DoesNotExist:
            return JsonResponse({"success": False, "error": "Notification not found"}, status=404)