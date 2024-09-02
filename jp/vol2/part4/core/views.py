from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import *


class HomeView(ListView):
    model = Room
    template_name = 'core/home.html'

    
class RoomView(DetailView):
    model = Room
    template_name = 'core/room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_list = Room.objects.all()
        context.update({'room_list': room_list})
        return context
