from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView

# Create your views here.
class HomeView(TemplateView):
    template_name = "core/home.html"


class ItemView(TemplateView):
    template_name = "core/item.html"


class CartView(TemplateView):
    template_name = "core/cart.html"


class OrderView(RedirectView):
    url = reverse_lazy('success')


class SuccessView(TemplateView):
    template_name = "core/success.html"
