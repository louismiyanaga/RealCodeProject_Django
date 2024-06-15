from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView, View

from .models import Item, CartItem, Order

# Create your views here.
User = get_user_model()


class OnlyYouMixin(UserPassesTestMixin):
    """
    Grant access only in one of the following cases:
    
    "user's pk matches pk in URL" or "user is superuser"
    """
    def test_func(self):
        user = self.request.user
        return (user.id == self.kwargs['pk']) or (user.is_superuser)
    

class HomeView(ListView):
    template_name = "core/home.html"
    model = Item


class ItemView(DetailView):
    template_name = "core/item.html"
    model = Item

    def get_success_url(self):
        """
        Get URL of user's cart page (/cart/user_pk/)
        """
        user_pk = self.request.user.id
        return reverse_lazy('cart', kwargs={'pk': user_pk}) # Instead of kwargs={...}, args=(user_pk,) can be used 
    
    def post(self, *args, **kwargs):
        """
        When 'Add to cart' button clicked (=POST request sent),
        add cart_item (item and quantity) to user's cart.
        Since DetailView have no post method, define new one.
        [Procedure]
        1. Obtain 'item_pk' and 'quantity' from POST request
        2. Create cart_item with obtained item_pk and quantity
        3. Add the cart_item to user's cart
        4. Redirect to user's cart page
        """
        # 1. Obtain 'item_pk' and 'quantity' from POST request
        item_pk = self.request.POST.get('item_pk')
        quantity = int(self.request.POST.get('quantity'))
        # 2. Create cart_item with obtained item_pk and quantity
        item = Item.objects.get(id=item_pk)
        cart_item = CartItem(item=item, quantity=quantity)
        # 3. Add the cart_item to user's cart
        user = self.request.user
        user.cart.add_cart_item(cart_item)
        # 4. Redirect to user's cart page
        return redirect(self.get_success_url())


class CartView(LoginRequiredMixin, OnlyYouMixin, DetailView):
    template_name = "core/cart.html"
    model = User
    context_object_name = 'cart'

    def get_object(self, queryset=None):
        """
        Override default get_object method of DetailView to return 'cart' object.
        If this is not done, it returns 'user' object, not 'cart' object, 
        because user model is specified to the above 'model' attribute.
        """
        user = super().get_object(queryset)
        return user.cart


class OrderView(View):
    def post(self, *args, **kwargs):
        """
        When 'Proceed to checkout' button clicked (=POST request sent),
        create order object and empty user's cart.
        [Procedure]
        1. Create order object
        2. Copy cart_items to order_items
        3. Reset cart contents
        4. Redirect to payment page
        """
        # 1. Create order object
        order_user = self.request.user
        order_cart = order_user.cart
        order_obj = Order.objects.create(
            user=order_user,
            order_price=order_cart.total_price,
        )
        # 2. Copy cart_items to order_items
        # you can also write in one line as follows: order_obj.order_items.add(*order_cart.cart_items.all())
        for cart_item in order_cart.cart_items.all():
            order_obj.order_items.add(cart_item)
        # 3. Reset cart contents
        order_cart.cart_items.clear()
        # 4. Redirect to payment page
        # Temporarily redirect to success page (edit later to redirect to external payment page)
        return redirect(reverse_lazy('success'))


class SuccessView(TemplateView):
    template_name = "core/success.html"
