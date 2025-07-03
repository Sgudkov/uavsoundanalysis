"""
WSGI config for uavmanage project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

from uavsoundanalysis.uavmanage.settings import CHANNEL_LAYERS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uavmanage.settings")



application = get_wsgi_application()
