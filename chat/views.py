# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from base.models import User
# from .models import Message
# from django.db.models import Q


# @login_required
# def chat_room(request, username):
#     selected_user = User.objects.get(username=username) 
#     chats = Message.objects.filter(Q(sender=request.user, receiver=selected_user) | 
#                                 Q(sender=selected_user, receiver=request.user)).order_by('timestamp')

    
#     search_query = request.GET.get('search', '') 
#     # users = User.objects.exclude(id=request.user.id) 
#     users = User.objects.filter(
#         Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
#     ).distinct()

#     # chats = Message.objects.filter(
#     #     (Q(sender=request.user) & Q(receiver__username=username
#     # )) |
#     #     (Q(receiver=request.user) & Q(sender__username=username
#     # ))
#     # )

#     if search_query:
#         chats = chats.filter(Q(content__icontains=search_query))  

#     # chats = chats.order_by('timestamp') 
#     user_last_messages = []

#     for user in users:
#         last_message = Message.objects.filter(
#             (Q(sender=request.user) & Q(receiver=user)) |
#             (Q(receiver=request.user) & Q(sender=user))
#         ).order_by('-timestamp').first()

#         user_last_messages.append({
#             'user': user,
#             'last_message': last_message
#         })

#     # Sort user_last_messages by the timestamp of the last_message in descending order
#     # user_last_messages.sort(
#     #     key=lambda x: x['last_message'].timestamp if x['last_message'] else None,
#     #     reverse=True
#     # )

#     return render(request, 'chat.html', {
#          'selected_user': selected_user, 
#         'username': username,
#         'chats': chats,
#         'users': users,
#         'user_last_messages': user_last_messages,
#         'search_query': search_query 
#     })
from django.contrib.auth.decorators import login_required
from base.models import User
from .models import Message
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

# @login_required
# def chat_room(request, username):
#     selected_user = get_object_or_404(User, username=username)
#     chats = Message.objects.filter(
#         Q(sender=request.user, receiver=selected_user) | 
#         Q(sender=selected_user, receiver=request.user),
#         is_deleted=False
#     ).order_by('timestamp')

#     search_query = request.GET.get('search', '')
#     users = User.objects.filter(
#         Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
#     ).distinct()

#     if search_query:
#         chats = chats.filter(Q(content__icontains=search_query))

#     user_last_messages = []
#     for user in users:
#         last_message = Message.objects.filter(
#             (Q(sender=request.user) & Q(receiver=user)) |
#             (Q(receiver=request.user) & Q(sender=user)),
#             is_deleted=False
#         ).order_by('-timestamp').first()
#         user_last_messages.append({
#             'user': user,
#             'last_message': last_message
#         })

#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         user_list = [
#             {
#                 "username": user.username,
#                 "avatar_url": user.avatar.url if user.avatar else "/static/default-avatar.png",
#                 "last_message": user_last_messages[i]['last_message'].content if user_last_messages[i]['last_message'] else "No messages yet",
#                 "timestamp": user_last_messages[i]['last_message'].timestamp.strftime("%H:%M") if user_last_messages[i]['last_message'] else "",
#                 "is_sender": user_last_messages[i]['last_message'].sender == request.user if user_last_messages[i]['last_message'] else False
#             } for i, user in enumerate(users)
#         ]
#         return JsonResponse({"users": user_list})

#     return render(request, 'chat.html', {
#         'selected_user': selected_user,
#         'username': username,
#         'chats': chats,
#         'users': users,
#         'user_last_messages': user_last_messages,
#         'search_query': search_query
#     })

@login_required
def chat_room(request, username):
    selected_user = get_object_or_404(User, username=username)
    chats = Message.objects.filter(
        Q(sender=request.user, receiver=selected_user) | 
        Q(sender=selected_user, receiver=request.user),
        is_deleted=False
    ).order_by('timestamp')

    search_query = request.GET.get('search', '')
    users = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user)),
            is_deleted=False
        ).order_by('-timestamp').first()
        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # chats QuerySet-ni JSON serializable formatga aylantirish
    chats_serialized = [
        {
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'timestamp': message.timestamp.isoformat(),
            'edited': message.edited,
            'is_deleted': message.is_deleted,
            'reply_to': message.reply_to.id if message.reply_to else None,
            'image': message.image.url if message.image else None,
            'video': message.video.url if message.video else None,
            'voice': message.voice.url if message.voice else None,
            'file': message.file.url if message.file else None,
        }
        for message in chats
    ]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_list = [
            {
                "username": user.username,
                "avatar_url": user.avatar.url if user.avatar else "/static/default-avatar.png",
                "last_message": user_last_messages[i]['last_message'].content if user_last_messages[i]['last_message'] else "No messages yet",
                "timestamp": user_last_messages[i]['last_message'].timestamp.strftime("%H:%M") if user_last_messages[i]['last_message'] else "",
                "is_sender": user_last_messages[i]['last_message'].sender == request.user if user_last_messages[i]['last_message'] else False
            } for i, user in enumerate(users)
        ]
        return JsonResponse({"users": user_list})

    return render(request, 'chat.html', {
        'selected_user': selected_user,
        'username': username,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'chats_serialized': chats_serialized,  # JSON serializable format
    })

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.method == "POST" and message.sender == request.user:
        new_content = request.POST.get('content')
        if new_content:
            message.previous_content = message.content
            message.content = new_content
            message.edited = True
            message.save()

            channel_layer = get_channel_layer()
            room_group_name = f"chat_{''.join(sorted([request.user.username, message.receiver.username]))}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'edit',
                    'sender': request.user.username,
                    'receiver': message.receiver.username,
                    'message': new_content,
                    'message_id': message.id,
                    'edited': True,
                    'previous_content': message.previous_content,
                }
            )
            return JsonResponse({
                'status': 'success',
                'content': new_content,
                'message_id': message.id,
                'previous_content': message.previous_content,
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid request or unauthorized'})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.method == "POST" and message.sender == request.user:
        message.is_deleted = True
        message.content = "[Deleted]"
        message.save()

        channel_layer = get_channel_layer()
        room_group_name = f"chat_{''.join(sorted([request.user.username, message.receiver.username]))}"
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'action': 'delete',
                'message_id': message.id,
                'is_deleted': True,
            }
        )
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request or unauthorized'})

@login_required
def reply_to_message(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            receiver = original_message.sender if original_message.receiver == request.user else original_message.receiver
            new_message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                reply_to=original_message
            )

            channel_layer = get_channel_layer()
            room_group_name = f"chat_{''.join(sorted([request.user.username, receiver.username]))}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'reply',
                    'sender': request.user.username,
                    'receiver': receiver.username,
                    'message': content,
                    'message_id': new_message.id,
                    'reply_to': message_id,
                    'reply_to_content': original_message.content
                }
            )
            return JsonResponse({'status': 'success', 'content': content, 'message_id': new_message.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt
def upload_media(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        action = request.POST.get("action")
        media_type = request.POST.get("type")

        if file and action == "media":
            file_path = default_storage.save(f"chat_{media_type}s/{file.name}", file)
            file_url = default_storage.url(file_path)
            return JsonResponse({"url": file_url, "type": media_type})
        return JsonResponse({"error": "Invalid request"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)