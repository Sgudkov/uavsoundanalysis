import asyncio
import base64
import glob
import inspect
import io
import json
import logging
import os
import sys
import time
import uuid
import wave
from shutil import which
from time import sleep

from django.contrib.auth.models import User
from moviepy import VideoFileClip
from pydub import AudioSegment
from asgiref.sync import sync_to_async, async_to_sync
from channels.auth import get_user
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.layers import get_channel_layer
from django.apps import apps

from uavanalysis.droneAnalyzer import DroneAnalyzer
from uavanalysis.tasks import triggerAlarm

Coordinates = apps.get_model('uavanalysis', 'Coordinates')

logger = logging.getLogger(__name__)


# sys.path.append('C:/ProgramData/chocolatey/bin')

# @sync_to_async
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
    """
    A class to handle websocket connections. This class is a subclass of
    channels.generic.websocket.AsyncWebsocketConsumer.

    The class is used to handle websocket connections from the client. When a
    client connects to the websocket, the 'connect' method is called. When the
    client disconnects from the websocket, the 'disconnect' method is called.

    The class also has methods to handle incoming messages from the client. The
    'receive' method is called when the client sends a message to the server.

    Attributes:
        room_group_name (str): The name of the room group to which the client
            will connect.
        channel_layer (channels.layers.ChannelLayer): The channel layer to be
            used for communication with the client.

    Methods:
        connect: Called when a client connects to the websocket.
        receive: Called when the client sends a message to the server.
        disconnect: Called when the client disconnects from the websocket.
        change_color: Called when the client sends a message with the action
            'change_color'.
        new_label: Called when the client sends a message with the action
            'new_label'.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = 'room_name'
        self.channel_layer = get_channel_layer()
        self.audio_start_time = None
        self.current_audio_file = None
        self.samplerate = 44100  # частота дискретизации
        self.channels = 1  # моно
        self.audio_chunks = []
        self.id = None

    def get_unique_id(self):
        self.id = str(uuid.uuid4())
        return self.id

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

        data_text: [dict]

        data_text = json.loads(text_data) if text_data else None
        data_bytes = bytes_data if bytes_data else None

        raw_path = self.scope['raw_path'].decode('utf-8')
        print('raw_path', raw_path)

        match raw_path:
            case '/ws/':
                if data_text.get('action', None) == 'change_color':
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'change_color',  # Define handler name
                            'coordinates': data_text.get('coordinates', None),
                            'color': data_text.get('color', None)
                        }
                    )
                    await self.send(data_text)
            case '/ws/audio':
                print('audio')
                audio_dict = json.loads(data_bytes.decode('utf-8'))
                print('audio_dict', audio_dict)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'audio_parse',  # Define handler name
                        'audio': audio_dict
                    }
                )

                # await self.send(bytes_data=data_bytes)

    # Define the event handlers for the room group

    async def change_color(self, event: dict):
        await self.send(text_data=json.dumps({
            'id': event.get('id', None),
            'color': event.get('color', None),
            'coordinates': event.get('coordinates', None),
        }))

    async def audio_parse(self, event: dict):
        print('audio_parse')
        data = event.get('audio', None).get('data', None)
        id = event.get('audio', None).get('id', None)
        print('id', id)

        if not data:
            return

        file_src = f'{os.getcwd()}\\audio\\{self.get_unique_id()}.webm'
        file_des = f'{os.getcwd()}\\audio\\{self.get_unique_id()}.wav'
        # file_src = f'{os.getcwd()}\\output_audio.webm'
        # file_des = f'{os.getcwd()}\\output_audio.wav'

        with open(file_src, 'wb') as f:
            f.write(data)

        # print('file_des', file_des)

        # AudioSegment.converter = 'ffmpeg/ffmpeg.exe'
        # AudioSegment.ffmpeg = 'ffmpeg/ffmpeg.exe'
        # print(AudioSegment.converter)
        # print('output_audio.webm', 'output_audio.wav')

        # audio_buffer = io.BytesIO(data)
        #
        # try:
        #     AudioSegment.from_file(audio_buffer).export(file_des, format="wav")
        # except Exception as e:
        #     print(e)

        # await self.send(text_data=json.dumps({
        #     'id': event.get('id', None),
        #     'color': event.get('color', None),
        #     'coordinates': event.get('coordinates', None),
        # }))


class MyThreadSocketConsumer(WebsocketConsumer):
    room_group_name = 'default'
    actions = {
        'change_color': 'change_color',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.id = str(uuid.uuid4())
        self.audio_chunks = []
        self.audio_chunks_removed = []
        self.recording_start_time = None
        self.recording_duration = 0
        self.max_duration = 2  # Max duration of recording in seconds
        self.start_audio_time = 0
        self.end_audio_time = 0

    def set_unique_id(self):
        self.id = str(uuid.uuid4())

    def connect(self):
        logger.info('Connect method called')

        self.start_audio_time = 0
        self.end_audio_time = 2000
        self.audio_chunks = []
        self.recording_start_time = None

        try:

            user: User = async_to_sync(get_user)(self.scope)
            if not user.is_authenticated:
                self.close()
                return

            self.accept()

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.send(text_data=json.dumps(
                {"action": "connected", "coordinates": get_updated_placemarks()}))

        except Exception as e:
            logger.error('Error in connect method: %s', e)
            self.close()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        self.close()

    def receive(self, text_data=None, bytes_data=None):
        data_text: [dict]
        data_bytes: [bytes]

        raw_path = self.scope['raw_path'].decode('utf-8')
        print('raw_path', raw_path)

        match self.scope['raw_path'].decode('utf-8'):
            case '/ws/':
                data_text = json.loads(text_data) if text_data else None
                if data_text.get('action', None) == 'change_color':
                    self.change_color({
                        'coordinates': data_text.get('coordinates', None),
                        'color': data_text.get('color', None)
                    })
            case '/ws/audio':
                print('audio')
                data_text = json.loads(text_data)
                audio_data = base64.b64decode(data_text['data'])
                self.audio_chunks.append(audio_data)
                self.audio_parse({'audio': audio_data, 'id': self.id})

    def audio_parse(self, data: dict):
        placemarks = data.get('placemarks', None)
        audio_data = data.get('audio', None)

        try:
            if self.recording_start_time is None:
                self.recording_start_time = time.time()
                self.recording_duration = 0

            self.recording_duration = time.time() - self.recording_start_time

            # Set start and end times for read from audio chunks
            if self.recording_duration > self.max_duration:
                self.start_audio_time += 2000
                self.end_audio_time += 2000

            print(self.start_audio_time, self.end_audio_time)

            # Collect audio chunks
            combined_audio = b''.join(self.audio_chunks)
            file_name = f'audio_{int(time.time())}.wav'
            file_path = os.path.join('audio', file_name)

            # Save temporary file
            with open(file_path, 'wb') as f:
                f.write(combined_audio)

            # Convert to wav
            converted_file_path = self.convert_to_wav(file_path)

            # Remove temporary file
            os.remove(file_path)

            droneAnalyzer = DroneAnalyzer(f'{os.getcwd()}\\audio')

            if droneAnalyzer.is_drone():
                coordinates = [x for x in placemarks if x['id'] == 1]

                # Trigger alarm for all clients of the 'default' group
                asyncio.run(triggerAlarm(None, coordinates))

            os.remove(converted_file_path)

        except Exception as e:
            print(e)

    def change_color(self, event: dict):
        self.send(text_data=json.dumps({
            'color': event.get('color', None),
            'coordinates': event.get('coordinates', None),
        }))

    def convert_to_wav(self, file_path):
        audio = AudioSegment.from_file(file_path)
        converted_path = file_path.replace('.wav', '_converted.wav')
        audio = audio[self.start_audio_time:self.end_audio_time]
        audio.export(converted_path, format="wav", bitrate="192k")
        return converted_path
