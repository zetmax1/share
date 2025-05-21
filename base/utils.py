# from functools import wraps
# from django.shortcuts import get_object_or_404
# from django.contrib import messages
# from django.shortcuts import redirect
# from .models import Room, User

# def private_room_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, pk, *args, **kwargs):
#         post = get_object_or_404(Room, id=pk)
#         if post.host.auth_status == "private" and request.user != post.host and request.user not in post.host.followers.all():
#             print(f"Followers: 464+4")
#             messages.error(request, "This post is private. You cannot access it.")
#             return redirect("home")
#         return view_func(request, pk, *args, **kwargs)
#     return _wrapped_view



from functools import wraps
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from .models import Room, User
from follow.models import Follow

def private_room_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, pk, *args, **kwargs):
        post = get_object_or_404(Room, id=pk)
        # Check if the post is private
        if post.host.auth_status == "private":
            # If user is not authenticated, redirect to home
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to access this post.")
                return redirect("home")
            # Allow the host to access their own post
            if request.user == post.host:
                return view_func(request, pk, *args, **kwargs)
            # Check if the user is a follower using the Follow model
            is_follower = Follow.objects.filter(
                follower=request.user,
                following=post.host,  # Changed 'followed' to 'following'
                status="accepted"
            ).exists()
            print(f"Requesting user: {request.user.id}, Host: {post.host.id}")
            print(f"Host followers: {list(post.host.followers.all())}")
            print(f"Is follower: {is_follower}")
            if not is_follower:
                messages.error(request, "This post is private. You cannot access it.")
                return redirect("home")
        # If the post is public or the user has access, proceed to the view
        return view_func(request, pk, *args, **kwargs)
    return _wrapped_view