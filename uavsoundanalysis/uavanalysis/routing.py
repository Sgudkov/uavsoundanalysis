from django.urls import path
from .consumers import MyWebSocketConsumer, MyThreadSocketConsumer

urlpatterns = [
    # path('ws/', MyWebSocketConsumer.as_asgi()),
    # path('ws/audio', MyWebSocketConsumer.as_asgi()),
    path('ws/', MyThreadSocketConsumer.as_asgi()),
    path('ws/audio', MyThreadSocketConsumer.as_asgi()),
]
