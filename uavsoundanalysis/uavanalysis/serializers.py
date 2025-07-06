from rest_framework import serializers


class TestAlarmSerializer(serializers.Serializer):
    placemarks = serializers.JSONField()
