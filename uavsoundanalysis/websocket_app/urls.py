from django.urls import path
from .consumers import MyWebSocketConsumer

urlpatterns = [
    path('ws/', MyWebSocketConsumer.as_asgi()),
]
