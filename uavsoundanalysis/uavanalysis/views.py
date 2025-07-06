import asyncio

from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import TestAlarmSerializer
from .tasks import triggerAlarm


# Create your views here.
def index(request):
    return render(request, 'index.html')


def myMap(request):
    return render(request, 'uavanalysis/map.html')


class TestAlarmView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TestAlarmSerializer

    def post(self, request):
        # print('TestAlarmView.post', request.__dict__)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            asyncio.run(triggerAlarm(request.user, data['placemarks']))
            return JsonResponse({"status": "success", "data": data})
        else:
            return JsonResponse({"status": "error", "errors": serializer.errors})
