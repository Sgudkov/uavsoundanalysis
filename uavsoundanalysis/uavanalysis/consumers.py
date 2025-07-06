import asyncio
import json
import logging
import pdb

from asgiref.sync import sync_to_async
from channels.auth import login, get_user
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.sessions import SessionMiddleware
from django.apps import apps
from django.contrib.auth.models import User

Coordinates = apps.get_model('uavanalysis', 'Coordinates')

logger = logging.getLogger(__name__)

@sync_to_async
def get_updated_placemarks():
    placemarks = []
    pla_list = Coordinates.objects.all()
    for p in pla_list:
        placemarks.append({
            'id': p.id,
            'latitude': p.latitude,
            'longitude': p.longitude,
            'label': p.label
        })

    return placemarks


class MyWebSocketConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = 'room_name'
        self.channel_layer = get_channel_layer()

    async def connect(self):
        logger.info('Connect method called')
        try:
            user = await get_user(self.scope)
            if user.is_authenticated:
                await self.accept()
                # Define the room group name to which the client will connect
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                # Send the initial set of placemarks
                await self.send(text_data=json.dumps(
                    {"action": "connected", "coordinates": await get_updated_placemarks()}))
            else:
                print('not auth', user)
                await self.close()
        except Exception as e:
            logger.error('Error in connect method: %s', e)

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        print('receive')
        data: [dict]
        data = json.loads(text_data)
        if data['action'] == 'change_color':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'change_color',  # Define handler name
                    'coordinates': data.get('coordinates', None),
                    'color': data.get('color', None)
                }
            )
            await self.send(data)
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_label',  # Define handler name
                    'title': data.get('title', None),
                    'longitude': data.get('longitude', None),
                    'latitude': data.get('latitude', None),
                }
            )
            await self.send(data)

    # Define the event handlers for the room group
    async def new_label(self, event: dict):
        await self.send(text_data=json.dumps({
            'title': event.get('title', None),
            'longitude': event.get('longitude', None),
            'latitude': event.get('latitude', None),
        }))

    async def change_color(self, event: dict):
        await self.send(text_data=json.dumps({
            'id': event.get('id', None),
            'color': event.get('color', None),
            'coordinates': event.get('coordinates', None),
        }))
