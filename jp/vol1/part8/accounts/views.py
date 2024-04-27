from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

from .forms import SignupForm

# Create your views here.
User = get_user_model()


class SignupView(CreateView):
    template_name = "registration/signup.html"
    model = User
    form_class = SignupForm
    success_url = reverse_lazy('signup_done')


class SignupDoneView(TemplateView):
    template_name = "registration/signup_done.html"
