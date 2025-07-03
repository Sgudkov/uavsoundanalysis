import asyncio

from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def index(request):
    return render(request, 'index.html')


def map(request):
    return render(request, 'uavanalysis/map.html')


def get_new_label_view(request):
    new_label = "Новое название метки"
    return JsonResponse({'label': new_label})
