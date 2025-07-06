import json
import asyncio
import logging

from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from websockets.asyncio.client import connect

from uavsoundanalysis.uavanalysis.consumers import MyWebSocketConsumer

logger = logging.getLogger(__name__)


async def triggerAlarm(user: User, coordinates: list[dict] = None):
    logger.info('Triggering alarm')
    try:
        print('Triggering alarm')
        if not user.is_authenticated:
            return
        channel = get_channel_layer()
        await channel.group_send(
            'room_name',
            {
                'type': 'change_color',  # Define handler name
                'user': user,
                'coordinates': coordinates,
                'color': "red"
            }
        )
        await channel.send(
            'room_name',
            {
                'type': 'change_color',  # Define handler name
                'user': user,
                'coordinates': coordinates,
                'color': "red"
            }
        )
    except Exception as e:
        logger.error('Error in triggerAlarm method: %s', e)
