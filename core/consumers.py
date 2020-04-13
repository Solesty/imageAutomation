import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # We're always going to accept the connection, though
        # we may close later based on other factors

        # Join room group
        # We could have allowed any one to join the group
        # from the connect, but we need verify everythig

        await self.channel_layer.group_add(
            "album_view",
            self.channel_name,
        )

        await self.accept()

    async def notify(self, event):
        """
        This handles calls elsewhere in this codebase that look like
                    channel_layer.group_send(group_name, {
                'type': 'notify',  # This routes it to this handler.
                'content': json_message,
            })

        Don't try to directly use send_json or anything; this
        decoupling will help you as things grow
        """

        print("Sending")
        print(event['content'])
        await self.send_json(event['content'])

    async def receive_json(self, content, **kwargs):
        """
        This handles data sent over the wire from the client.

        We need to validate that the received data is of the correct
        form. You can do this with a simple DRF serializer

        We then need to use that validated data to confirm that the
        requesting user (avaiable in self.scope['user] because of
        the use of channels.auth.AuthMiddlewareStack in routing) is
        allowed to subscribe to the requested object.
        """

        group_name = "album_view"
        # The AsyncJsonWebsocketConsumer parent class has
        # self.groups list already. It uses it in cleanup

        print(self.groups)

        self.groups.append(group_name)
        # This actually subscribes the requesting socket to the
        # named group;
        await self.channel_layer.group_add(
            group_name,
            self.channel_name,
        )

        await self.notify({
            'type': 'notify',
            'content': content
        })


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        print(self.room_group_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        print(message)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
