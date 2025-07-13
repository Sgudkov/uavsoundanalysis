import json
import asyncio
import logging

from channels.layers import get_channel_layer
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


async def triggerAlarm(user: User = None, coordinates: list[dict] = None):
    """
    Trigger an alarm for all clients connected to the 'room_name' group.

    Args:
        user (User): The user for which to trigger the alarm.
        coordinates (list[dict], optional): The coordinates of the placemarks to highlight. Defaults to None.
    """
    logger.info('Triggering alarm')

    try:
        print('Triggering alarm')
        channel = get_channel_layer()
        data_send = {
            'type': 'change_color',  # Define handler name
            'user': user,
            'coordinates': coordinates,
            'color': "red"
        }
        await channel.group_send(
            'default',
            data_send
        )
        await channel.send(
            'default',
            data_send
        )
    except Exception as e:
        logger.error('Error in triggerAlarm method: %s', e)
