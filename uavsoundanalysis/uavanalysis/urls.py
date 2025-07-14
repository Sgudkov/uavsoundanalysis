from django.urls import path

from . import views

urlpatterns = [
    path("", views.myMap, name="map"),
    path("test_alarm", views.TestAlarmView.as_view(), name="test_alarm"),
]
