import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from company.middleware import JwtAuthMiddlewareStack


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from company import routing


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JwtAuthMiddlewareStack(
            URLRouter(routing.websocket_urlpatterns)
        ),
    }
)
