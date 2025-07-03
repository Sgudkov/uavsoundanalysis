import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


async def get_updated_placemarks():
    # Здесь должен быть код для получения данных о метке
    # Например, запрос к базе данных
    placemarks = [
        {
            "id": 1,
            "latitude": 59.46,
            "longitude": 31.62,
            "label": "Метка 1",
        },
        {
            "id": 2,
            "latitude": 59.47,
            "longitude": 31.62,
            "label": "Метка 2",
        },
        {
            "id": 3,
            "latitude": 59.48,
            "longitude": 31.62,
            "label": "Метка 3",
        },
        {
            "id": 4,
            "latitude": 59.49,
            "longitude": 31.62,
            "label": "Метка 4",
        },
    ]
    return placemarks


class MyWebSocketConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = 'room_name'
        self.channel_layer = get_channel_layer()

    async def connect(self):
        # Define the room group name to which the client will connect
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send the initial set of placemarks
        await self.send(text_data=json.dumps(
            {"action": "connected", "coordinates": await get_updated_placemarks()}))

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data['action'] == 'change_color':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'change_color',  # Define handler name
                    'id': data.get('id', None),
                    'color': data.get('color', None),
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
        }))
