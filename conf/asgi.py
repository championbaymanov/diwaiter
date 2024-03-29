import os

import django
import environ
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from src.ws.orders import routing

env = environ.Env()
env.read_env(".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))
django.setup()

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))),
        "websocket": URLRouter(routing.websocket_urlpatterns)
    }
)
