"""
ASGI config for uavmanage project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.auth import AuthMiddlewareStack

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from uavsoundanalysis.websocket_app.urls import urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uavmanage.settings")
#django.setup()
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(urlpatterns)),
        # Just HTTP for now. (We can add other protocols later.)
    }
)
