import asyncio
import base64
import json
import logging
import os
import time
import uuid

from asgiref.sync import async_to_sync
from channels.auth import get_user
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from pydub import AudioSegment

from uavanalysis.droneAnalyzer import DroneAnalyzer
from uavanalysis.models import Coordinates
from uavanalysis.tasks import triggerAlarm

logger = logging.getLogger(__name__)


def get_updated_placemarks():
    placemarks = []
    pla_list = Coordinates.objects.all()
    for p in pla_list:
        placemarks.append(
            {
                "id": p.id,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "label": p.label,
            }
        )

    return placemarks


class MyThreadSocketConsumer(WebsocketConsumer):
    room_group_name = "default"
    actions = {
        "change_color": "change_color",
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
        self.alarm_triggered = False

    def connect(self):
        logger.info("Connect method called")

        self.start_audio_time = 0
        self.end_audio_time = 2000
        self.audio_chunks = []
        self.recording_start_time = None
        self.alarm_triggered = False

        try:

            user: User = async_to_sync(get_user)(self.scope)
            if not user.is_authenticated:
                self.close()
                return

            self.accept()

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )

            self.send(
                text_data=json.dumps(
                    {"action": "connected", "coordinates": get_updated_placemarks()}
                )
            )

        except Exception as e:
            logger.error("Error in connect method: %s", e)
            self.close()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

        self.close()

    def receive(self, text_data=None, bytes_data=None):
        data_text: [dict]
        data_bytes: [bytes]

        match self.scope["raw_path"].decode("utf-8"):
            case "/ws/":
                data_text = json.loads(text_data) if text_data else None
                if data_text.get("action", None) == "change_color":
                    self.change_color(
                        {
                            "coordinates": data_text.get("coordinates", None),
                            "color": data_text.get("color", None),
                        }
                    )
            case "/ws/audio":
                data_text = json.loads(text_data)
                audio_data = base64.b64decode(data_text["data"])
                self.audio_parse(
                    {
                        "audio": audio_data,
                        "placemarks": data_text.get("placemarks", None),
                    }
                )

    def audio_parse(self, data: dict):
        placemarks = data.get("placemarks", None)
        audio_data = data.get("audio", None)

        self.audio_chunks.append(audio_data)

        try:
            if self.recording_start_time is None:
                self.recording_start_time = time.time()
                self.recording_duration = 0

            self.recording_duration = time.time() - self.recording_start_time

            # Set start and end times for read from audio chunks
            if self.recording_duration > self.max_duration:
                self.start_audio_time += 2000
                self.end_audio_time += 2000

            # Collect audio chunks
            combined_audio = b"".join(self.audio_chunks)
            file_name = f"audio_{int(time.time())}.wav"
            file_path = os.path.join("audio", file_name)

            # Save temporary file
            with open(file_path, "wb") as f:
                f.write(combined_audio)

            # Convert to wav
            converted_file_path = self.convert_to_wav(file_path)
            # Remove temporary file
            os.remove(file_path)

            droneAnalyzer = DroneAnalyzer(converted_file_path)

            # Check if it is a drone and trigger alarm
            if droneAnalyzer.is_drone() and not self.alarm_triggered:
                # For test use only one placemark
                coordinates = [x for x in placemarks if x["id"] == 1]

                # Trigger alarm for all clients of the 'default' group
                asyncio.run(triggerAlarm(None, coordinates))

                self.alarm_triggered = True

            # Remove converted file
            os.remove(converted_file_path)

        except Exception as e:
            print(e)

    def change_color(self, event: dict):
        self.send(
            text_data=json.dumps(
                {
                    "color": event.get("color", None),
                    "coordinates": event.get("coordinates", None),
                }
            )
        )

    def convert_to_wav(self, file_path):
        audio = AudioSegment.from_file(file_path)
        converted_path = file_path.replace(".wav", "_converted.wav")
        audio = audio[self.start_audio_time : self.end_audio_time]
        audio.export(converted_path, format="wav", bitrate="192k")
        return converted_path
