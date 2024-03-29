from ..base import BaseConsumer


class ClientOrderConsumer(BaseConsumer):
    room_group_name = 'client_order'

    async def connect(self):
        print(self.scope['url_route'])
        channel_name = 'asd'

        await self.channel_layer.group_add(
            self.room_group_name,
            channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

