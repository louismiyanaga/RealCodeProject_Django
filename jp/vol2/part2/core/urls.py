from django.urls import path

from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('room/', RoomView.as_view(), name='room'),
]
