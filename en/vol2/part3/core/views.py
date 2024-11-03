from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'

    
class RoomView(TemplateView):
    template_name = 'core/room.html'
