from django.urls import path

from . import views
from .consumers import MyWebSocketConsumer

urlpatterns = [
    path("", views.myMap, name="index"),
    path('ws/', MyWebSocketConsumer.as_asgi()),
    path('ws/audio', MyWebSocketConsumer.as_asgi()),
    path('test_alarm', views.TestAlarmView.as_view(), name='test_alarm')
]
