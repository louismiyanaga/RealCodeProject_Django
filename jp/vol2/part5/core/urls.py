from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('room/<int:pk>/', login_required(RoomView.as_view()), name='room'),
]
