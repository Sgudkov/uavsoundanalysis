import asyncio
import os
import time

from django.contrib.auth.models import User
from pydub import AudioSegment

from ..droneAnalyzer.drone_analyzer import DroneAnalyzer
from ..tasks import triggerAlarm


class AudioParser:
    """
    Class for parsing audio data.

    The class is used to parse audio data from websocket and save it to chunks.
    It also checks if the audio is a drone sound and triggers an alarm if it is.

    Attributes:
        audio_chunks (list): List of saved audio chunks.
        audio_chunks_removed (list): List of audio chunks that are already sent to drone analyzer.
        recording_start_time (float): Time when recording started.
        recording_duration (float): Duration of recording.
        max_duration (int): Max duration of recording in seconds.
        start_audio_time (int): Start time of the audio chunk that is being analyzed.
        end_audio_time (int): End time of the audio chunk that is being analyzed.
        alarm_triggered (bool): Flag if alarm is already triggered.

    Methods:
        parse(data): Method to parse audio data from websocket.
        _convert_to_wav(file_path): Method to convert audio chunk to wav format.
    """

    def __init__(self):
        self.audio_chunks = []
        self.audio_chunks_removed = []
        self.recording_start_time = None
        self.recording_duration = 0
        self.max_duration = 2  # Max duration of recording in seconds
        self.start_audio_time = 0
        self.end_audio_time = 0
        self.alarm_triggered = False

    def init_data(self):
        self.start_audio_time = 0
        self.end_audio_time = 2000
        self.audio_chunks = []
        self.recording_start_time = None
        self.alarm_triggered = False

    def parse(self, data: dict):
        placemarks: list = data.get("placemarks", [])
        audio_data = data.get("audio", None)

        # Collect audio chunks
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

            # Set audio chunks to byte string
            combined_audio = b"".join(self.audio_chunks)
            file_name = f"audio_{int(time.time())}.wav"
            file_path = os.path.join("audio", file_name)

            # Save temporary file
            with open(file_path, "wb") as f:
                f.write(combined_audio)

            # Convert to wav
            converted_file_path = self._convert_to_wav(file_path)

            # Remove temporary file
            os.remove(file_path)

            droneAnalyzer = DroneAnalyzer(converted_file_path)

            # Check if it is a drone and trigger alarm
            if droneAnalyzer.is_drone() and not self.alarm_triggered:
                # For test use only one placemark
                coordinates = [x for x in placemarks if x["id"] == 1]

                # Trigger alarm for all clients of the 'default' group
                asyncio.run(triggerAlarm(User(), coordinates))

                self.alarm_triggered = True

            # Remove converted file
            os.remove(converted_file_path)

        except Exception as e:
            print(e)

    def _convert_to_wav(self, file_path):
        audio = AudioSegment.from_file(file_path)
        converted_path = file_path.replace(".wav", "_converted.wav")
        audio = audio[self.start_audio_time: self.end_audio_time]
        audio.export(converted_path, format="wav", bitrate="320k", parameters=["-ac", "1", "-ar", "48000"])
        return converted_path
