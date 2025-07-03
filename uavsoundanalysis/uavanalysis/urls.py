from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from . import views
from uavsoundanalysis.websocket_app.urls import urlpatterns

urlpatterns = [
    path("", views.index, name="index"),
    path("map", views.map, name="map"),
    path('get_new_label/', views.get_new_label_view, name='get_new_label'),
]
