from django.urls import re_path, path

from src.ws.orders.consumers import ClientOrderConsumer

websocket_urlpatterns = [
    # re_path(r"^ws/chat/(?P<room_name>\w+)/$", ClientOrderConsumer.as_asgi()),
    # re_path(r"^ws/chat", ClientOrderConsumer.as_asgi()),
    path("ws/chat/<str:room_name>/", ClientOrderConsumer.as_asgi()),
]
