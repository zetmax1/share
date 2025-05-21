
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from base.models import User
# from .models import Message

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.user = self.scope['user']
#         user2 = self.room_name
#         self.room_group_name = f"chat_{''.join(sorted([self.user.username, user2]))}"

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         self.user_group_name = f"user_{self.user.username}"
#         await self.channel_layer.group_add(self.user_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#         await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         action = data.get('action')
#         message = data.get('message')
#         message_id = data.get('message_id')
#         reply_to = data.get('reply_to')
#         receiver = await self.get_receiver_user()

#         if action == 'send':
#             await self.save_message(self.user, receiver, message)
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'action': 'send',
#                     'sender': self.user.username,
#                     'receiver': receiver.username,
#                     'message': message,
#                     'message_id': None,
#                     'reply_to': None
#                 }
#             )
#         elif action == 'edit' and message_id:
#             await self.handle_edit(message_id, message)
#         elif action == 'reply' and reply_to:
#             await self.handle_reply(reply_to, message)
#         elif action == 'delete_request' and message_id:
#             await self.handle_delete_request(message_id)
#         elif action == 'delete_confirm' and message_id:
#             await self.handle_delete_confirm(message_id)

#         # Update chat list for both users
#         await self.channel_layer.group_send(f"user_{receiver.username}", {"type": "update_chat_list"})
#         await self.channel_layer.group_send(f"user_{self.user.username}", {"type": "update_chat_list"})

#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps(event))

#     async def update_chat_list(self, event):
#         await self.send(text_data=json.dumps({"type": "update_chat_list"}))

#     @sync_to_async
#     def save_message(self, sender, receiver, message):
#         return Message.objects.create(sender=sender, receiver=receiver, content=message)

#     async def handle_edit(self, message_id, new_content):
#         message = await self.edit_message(message_id, new_content)
#         if message:
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'action': 'edit',
#                     'sender': self.user.username,
#                     'receiver': message.receiver.username,
#                     'message': new_content,
#                     'message_id': message_id,
#                     'edited': True
#                 }
#             )

#     # async def handle_edit(self, message_id, new_content):
#     #     message = await self.edit_message(message_id, new_content)
#     #     if message:
#     #         await self.channel_layer.group_send(
#     #             self.room_group_name,
#     #             {
#     #                 'type': 'chat_message',
#     #                 'action': 'edit',
#     #                 'sender': self.user.username,
#     #                 'receiver': message.receiver.username,
#     #                 'message': new_content,
#     #                 'message_id': message_id,
#     #                 'edited': True
#     #             }
#     #         )

#     # async def handle_reply(self, reply_to_id, message_content):
#     #     reply_message = await self.reply_to_message(reply_to_id, message_content)
#     #     if reply_message:
#     #         await self.channel_layer.group_send(
#     #             self.room_group_name,
#     #             {
#     #                 'type': 'chat_message',
#     #                 'action': 'reply',
#     #                 'sender': self.user.username,
#     #                 'receiver': reply_message.receiver.username,
#     #                 'message': message_content,
#     #                 'message_id': reply_message.id,
#     #                 'reply_to': reply_to_id
#     #             }
#     #         )
#     async def handle_reply(self, reply_to_id, message_content):
#         reply_message = await self.reply_to_message(reply_to_id, message_content)
#         if reply_message:
#             # Fetch the original message content
#             original_message = await sync_to_async(Message.objects.get)(id=reply_to_id)
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'action': 'reply',
#                     'sender': self.user.username,
#                     'receiver': reply_message.receiver.username,
#                     'message': message_content,
#                     'message_id': reply_message.id,
#                     'reply_to': reply_to_id,
#                     'reply_to_content': original_message.content  # Add this
#                 }
#             )

#     async def handle_delete_request(self, message_id):
#         message = await sync_to_async(Message.objects.get)(id=message_id)
#         if message.sender == self.user:
#             await self.send(text_data=json.dumps({
#                 'type': 'delete_confirmation',
#                 'message_id': message_id,
#                 'message': 'Are you sure you want to delete this message?'
#             }))

#     async def handle_delete_confirm(self, message_id):
#         message = await self.delete_message(message_id)
#         if message:
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'action': 'delete',
#                     'message_id': message_id
#                 }
#             )

#     @sync_to_async
#     def edit_message(self, message_id, new_content):
#         message = Message.objects.get(id=message_id)
#         if message.sender == self.user:  # Security check
#             message.content = new_content
#             message.edited = True
#             message.save()
#             return message
#         return None

#     @sync_to_async
#     def reply_to_message(self, reply_to_id, message_content):
#         original_message = Message.objects.get(id=reply_to_id)
#         receiver = original_message.sender if original_message.receiver == self.user else original_message.receiver
#         reply_message = Message.objects.create(
#             sender=self.user,
#             receiver=receiver,
#             content=message_content,
#             reply_to=original_message
#         )
#         return reply_message

#     @sync_to_async
#     def delete_message(self, message_id):
#         message = Message.objects.get(id=message_id)
#         if message.sender == self.user:  # Security check
#             message.is_deleted = True  # Soft deletion
#             message.save()
#             return message
#         return None

#     @sync_to_async
#     def get_receiver_user(self):
#         return User.objects.get(username=self.room_name)


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from base.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Resolve UserLazyObject to a real User instance
        self.user = await self.get_user(self.scope['user'])
        if not self.user.is_authenticated:  # Ensure the user is logged in
            await self.close()
            return
        user2 = self.room_name
        self.room_group_name = f"chat_{''.join(sorted([self.user.username, user2]))}"
        self.user_group_name = f"user_{self.user.username}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Only attempt to discard groups if they were set
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        message = data.get('message')
        message_id = data.get('message_id')
        reply_to = data.get('reply_to')
        receiver = await self.get_receiver_user()
        if not receiver:  # Handle case where receiver doesn't exist
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Receiver not found'}))
            return

        if action == 'send':
            new_message = await self.save_message(self.user, receiver, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'send',
                    'sender': self.user.username,
                    'receiver': receiver.username,
                    'message': message,
                    'message_id': new_message.id,
                    'reply_to': None
                }
            )
        elif action == 'edit' and message_id:
            await self.handle_edit(message_id, message)
        elif action == 'reply' and reply_to:
            await self.handle_reply(reply_to, message)
        elif action == 'delete_request' and message_id:
            await self.handle_delete_request(message_id)
        elif action == 'delete_confirm' and message_id:
            await self.handle_delete_confirm(message_id)
        elif action == 'media':
            media_type = data.get('type')
            url = data.get('url')
            filename = data.get('filename')
            new_message = await self.save_media_message(self.user, receiver, media_type, url)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'media',
                    'sender': self.user.username,
                    'receiver': receiver.username,
                    'message_id': new_message.id,
                    'type': media_type,
                    'url': url,
                    'filename': filename
                }
            )

        # Notify both users to update their chat list
        await self.channel_layer.group_send(f"user_{receiver.username}", {"type": "update_chat_list"})
        await self.channel_layer.group_send(f"user_{self.user.username}", {"type": "update_chat_list"})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def update_chat_list(self, event):
        await self.send(text_data=json.dumps({"type": "update_chat_list"}))

    @sync_to_async
    def get_user(self, user):
        """Resolve UserLazyObject to a User instance."""
        if hasattr(user, '_wrapped') and hasattr(user, '_setupfunc'):
            return user._wrapped
        return user

    @sync_to_async
    def save_message(self, sender, receiver, message):
        return Message.objects.create(sender=sender, receiver=receiver, content=message)

    @sync_to_async
    def save_media_message(self, sender, receiver, media_type, url):
        message = Message(sender=sender, receiver=receiver)
        if media_type == "image":
            message.image = url
        elif media_type == "video":
            message.video = url
        elif media_type == "voice":
            message.voice = url
        elif media_type == "file":
            message.file = url
        message.save()
        return message

    async def handle_edit(self, message_id, new_content):
        message = await self.edit_message(message_id, new_content)
        if message:
            reply_to_content = await sync_to_async(lambda: message.reply_to.content if message.reply_to else None)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'edit',
                    'sender': self.user.username,
                    'receiver': message.receiver.username,
                    'message': new_content,
                    'message_id': message_id,
                    'edited': True,
                    'previous_content': message.previous_content,
                    'reply_to': message.reply_to.id if message.reply_to else None,
                    'reply_to_content': reply_to_content
                }
            )

    async def handle_delete_request(self, message_id):
        await self.send(text_data=json.dumps({
            'type': 'delete_request',
            'message_id': message_id
        }))

    async def handle_delete_confirm(self, message_id):
        message = await self.delete_message(message_id)
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete',
                    'message_id': message_id,
                    'is_deleted': True
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to delete the message.'
            }))

    @sync_to_async
    def edit_message(self, message_id, new_content):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender == self.user:
                message.previous_content = message.content
                message.content = new_content
                message.edited = True
                message.save()
                return message
            return None
        except Message.DoesNotExist:
            return None

    @sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender == self.user:
                message.is_deleted = True
                message.content = "[Deleted]"
                message.save()
                return message
            return None
        except Message.DoesNotExist:
            return None

    async def handle_reply(self, reply_to_id, message_content):
        reply_message = await self.reply_to_message(reply_to_id, message_content)
        if reply_message:
            original_message = await sync_to_async(Message.objects.get)(id=reply_to_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'reply',
                    'sender': self.user.username,
                    'receiver': reply_message.receiver.username,
                    'message': message_content,
                    'message_id': reply_message.id,
                    'reply_to': reply_to_id,
                    'reply_to_content': original_message.content
                }
            )

    @sync_to_async
    def reply_to_message(self, reply_to_id, message_content):
        try:
            original_message = Message.objects.get(id=reply_to_id)
            receiver = original_message.sender if original_message.receiver == self.user else original_message.receiver
            reply_message = Message.objects.create(
                sender=self.user,
                receiver=receiver,
                content=message_content,
                reply_to=original_message
            )
            return reply_message
        except Message.DoesNotExist:
            return None

    @sync_to_async
    def get_receiver_user(self):
        try:
            return User.objects.get(username=self.room_name)
        except User.DoesNotExist:
            return None




