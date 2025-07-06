from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from . import views
from .consumers import MyWebSocketConsumer

urlpatterns = [
    path("", views.index, name="index"),
    path("map", views.myMap, name="map"),
    path('ws/', MyWebSocketConsumer.as_asgi()),
    path('test_alarm', views.TestAlarmView.as_view(), name='test_alarm')
]
