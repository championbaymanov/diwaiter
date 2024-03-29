import inspect
from typing import Union

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet

# from src.chat.base.exceptions import NotFound, PermissionDenied, ValidationError
# from src.chat.base.utils import Notify, catch_exception
from channels.exceptions import StopConsumer


class BaseConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(BaseConsumer, self).__init__(*args, **kwargs)
        self.room_name = "unauthorized"
        self.room_group_name = "unauthorized_group"

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close(3000)
            raise StopConsumer()


    # def getattribute(self, name):
    #     value = object.getattribute(self, name)
    #     if inspect.ismethod(value):
    #         return catch_exception(value)
    #     return value

#
# class BaseHandler:
#     queryset: Union[QuerySet, None] = None
#     lookup_field = "id"
#     internal = False
#
#     def init(self, request, websocket):
#         self._model_object = None
#         self.request = request
#         self.websocket = websocket
#
#     async def handle(self):
#         permission: bool = await self.check_permissions()
#         if not permission:
#             raise PermissionDenied()
#         response = await self.main(self.request)
#         await self.make_response(response)
#
#     async def make_response(self, response):
#         if response:
#             notify = Notify(data=response.data)
#             await self.respond(notify.as_success_response)
#             await self.group_send(response.other, notify.as_success_response)
#             await self.group_send(response.me, notify.as_success_response, exclude_current=True)
#
#     async def respond(self, content):
#         content["action"] = self.request.action
#         await self.websocket.send_json(content)
#
#     async def group_send(self, user, content, exclude=None, exclude_current=False):
#         if exclude is None:
#             exclude = []
#
#         if exclude_current is None:
#             exclude += [self.websocket.channel_name]
#
#         if content.get("action") is None:
#             content["action"] = self.request.action
#
#         layer = get_channel_layer()
#         await layer.group_send(f"user_{user.id}", {"type": "group.receive", "content": content, "exclude": exclude})
#
#     @database_sync_to_async
#     async def check_permissions(self):
#         """Надо реализовать."""
#         return True
#
#     async def get_object(self, related_fields: list = None, cached=True):
#         try:
#             if cached and self._model_object:
#                 return self._model_object
#             self._model_object = await database_sync_to_async(self.queryset.get)(id=self.request.data.get(self.lookup_field))
#             return self._model_object
#         except ObjectDoesNotExist as e:
#             raise NotFound(e)
#
#     @database_sync_to_async
#     def validate_serializer(self, serializer):
#         if not serializer.is_valid():
#             raise ValidationError(serializer.errors)
