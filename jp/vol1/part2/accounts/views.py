from django.views.generic.base import TemplateView

# Create your views here.
class SignupView(TemplateView):
    template_name = "registration/signup.html"


class SignupDoneView(TemplateView):
    template_name = "registration/signup_done.html"
