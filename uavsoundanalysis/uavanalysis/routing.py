from django.urls import path

from .consumers import MyThreadSocketConsumer

urlpatterns = [
    path("ws/", MyThreadSocketConsumer.as_asgi()),
    path("ws/audio", MyThreadSocketConsumer.as_asgi()),
]
