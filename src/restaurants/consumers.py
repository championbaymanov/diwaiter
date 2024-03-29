import json

from channels.exceptions import StopConsumer

from src.ws.base import BaseConsumer


class ClientOrderConsumer(BaseConsumer):
    room_group_name = 'client_order'

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close(3000)
            raise StopConsumer()

        self.room_name = self.scope["user"].id

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # await self.change_online
        print(f"CONNECTED --> CHANNEL_NAME: {self.channel_name}")
        print("Socket Connection could not be made")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receive message from WebSocket.

        Get the event and send the appropriate event
        """
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", None)

            await self.channel_layer.group_send(self.room_group_name, {"type": "send_message", "message": message})
        except Exception:
            await self.send_json({"response": "Invalid data format"})

    async def chat_message(self, event):
        """Receive message from room group."""
        message = event.get("message", None)

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                }
            )
        )