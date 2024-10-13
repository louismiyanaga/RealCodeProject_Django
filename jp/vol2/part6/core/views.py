import json

from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from .models import *
from .forms import *


class HomeView(ListView):
    model = Room
    template_name = 'core/home.html'

    
class RoomView(DetailView, FormMixin):
    model = Room
    template_name = 'core/room.html'
    form_class = ReservationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_list = Room.objects.all()
        context.update({'room_list': room_list})

        room_pk = self.kwargs.get('pk')
        reservation_qs = Reservation.objects.filter(room_id=room_pk)
        events = []
        for reservation in reservation_qs:
            event = {
                'title': reservation.title,
                'start': reservation.start_time.isoformat(timespec='seconds'),
                'end': reservation.end_time.isoformat(timespec='seconds'),
                'backgroundColor': '#0d6efd',
                'borderColor': '#0d6efd',
            }
            events.append(event)
        context.update({'events': json.dumps(events)})

        return context

    def post(self, *args, **kwargs):
        form = ReservationForm(self.request.POST)
        if form.is_valid:
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_success_url(self):
        room_pk = self.kwargs.get('pk')
        return reverse_lazy('room', args=(room_pk,))