import asyncio

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import TestAlarmSerializer
from .tasks import triggerAlarm


def myMap(request):
    return render(request, "map.html")


class TestAlarmView(APIView):
    """
    API endpoint for test alarm.

    To be used for testing alarm trigger.

    POST data format:
    {
        "placemarks": [
            {
                "id": "some_id",
                "latitude": 0.0,
                "longitude": 0.0
            }
        ]
    }
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TestAlarmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            asyncio.run(triggerAlarm(request.user, data["placemarks"]))
            return JsonResponse({"status": "success", "data": data})
        else:
            return JsonResponse({"status": "error", "errors": serializer.errors})
