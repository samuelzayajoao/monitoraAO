# chat/consumers.py
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from ..projects.models import Collaborator

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        collaborator = (
            await Collaborator.objects.select_related("project")
            .filter(project__view_key=self.room_name)
            .afirst()
        )

        if not collaborator:
            await self.close()
            raise ValueError("Nao e um colaborador")

        await sync_to_async(print)(collaborator.project.view_key)
        self.room_group_name = f"chat_{collaborator.project.view_key}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def sale_event(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps({"type": "sale_event", "data": data}))
