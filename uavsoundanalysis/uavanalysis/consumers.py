import base64
import json
import logging

from asgiref.sync import async_to_sync
from channels.auth import get_user
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from uavanalysis.audioParser.audio_parser import AudioParser
from uavanalysis.models import Coordinates

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
        self.audioParser = AudioParser()

    def connect(self):
        logger.info("Connect method called")
        self.audioParser.init_data()

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

    # Define event handlers
    def audio_parse(self, data: dict):

        # Parse audio data and trigger alarm if it is a drone sound
        self.audioParser.parse(data)

    def change_color(self, event: dict):
        self.send(
            text_data=json.dumps(
                {
                    "color": event.get("color", None),
                    "coordinates": event.get("coordinates", None),
                }
            )
        )
