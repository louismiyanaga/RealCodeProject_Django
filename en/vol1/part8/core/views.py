from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.base import TemplateView, View

import stripe

from .forms import SearchForm
from .models import Item, CartItem, Order

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY


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
    paginate_by = 6

    def get_context_data(self, **kwargs):
        """
        Override default get_context_data method of ListView to
        add form to context to make {{ form }} available in template
        """
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm
        return context

    def get_queryset(self):
        """
        Override default get_queryset method of ListView to
        extract specific items that are in requested category 
        """
        items = super().get_queryset()
        q_category = self.request.GET.get('category')
        if q_category is not None:
            items = items.filter(category=q_category)
        return items


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


class DeleteCartItemView(LoginRequiredMixin, OnlyYouMixin, DeleteView):
    model = User

    def get_object(self, queryset=None):
        """
        Override default get_object method of DeleteView so that specific
        'cart_item' object is returned and targeted for deletion.
        If this is not done, it returns 'user' object, not 'cart_item' object, 
        because user model is specified to the above 'model' attribute.
        [Procedure]
        1. Obtain cart_item's pk from POST request
        2. Retrieve one cart_item that matches the pk from cart
        """
        user = super().get_object(queryset)
        # 1. Obtain cart_item's pk from POST request
        cart_item_pk = self.request.POST['cart_item_pk']
        # 2. Retrieve one cart_item that matches the pk from cart
        cart_item = user.cart.cart_items.get(id=cart_item_pk)
        return cart_item
    
    def get_success_url(self):
        """
        Get URL of user's cart page (/cart/user_pk/)
        """
        user_pk = self.request.user.id
        return reverse_lazy('cart', kwargs={'pk': user_pk}) # Instead of kwargs={...}, args=(user_pk,) can be used 


class OrderView(View):
    def post(self, *args, **kwargs):
        """
        When 'Proceed to checkout' button clicked (=POST request sent),
        TWO main processes are executed.

        1. On Django Side
        2. On Stripe Side

        """
        
        """
        --------------------------------------------------------------
        1. On Django Side
        --------------------------------------------------------------
        
        Create order object and empty user's cart.
        [Procedure]
        1-1. Create order object
        1-2. Copy cart_items to order_items
        1-3. Reset cart contents
        """
        # 1-1. Create order object
        order_user = self.request.user
        order_cart = order_user.cart
        order_obj = Order.objects.create(
            user=order_user,
            order_price=order_cart.total_price,
        )
        # 1-2. Copy cart_items to order_items
        # you can also write in one line as follows: order_obj.order_items.add(*order_cart.cart_items.all())
        for cart_item in order_cart.cart_items.all():
            order_obj.order_items.add(cart_item)
        # 1-3. Reset cart contents
        order_cart.cart_items.clear()

        """
        --------------------------------------------------------------
        2. On Stripe Side
        --------------------------------------------------------------
        
        Direct user to Stripe-hosted payment page.
        [Procedure]
        2-1. Prepare line_items (a list of purchased items)
        2-2. Create checkout_session
        2-3. Direct to payment page
        """
        # 2-1. Prepare line_items
        line_items = []
        for order_item in order_obj.order_items.all():
            line_item = {
                'price_data': {
                    'currency': 'usd', # three-letter currency codes
                    'unit_amount': int(order_item.item.price*100), # in cents
                    'product_data': {
                        'name': order_item.item.name,
                    }
                },
                'quantity': order_item.quantity,
            }
            line_items.append(line_item)
        # 2-2. Create checkout_session
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                phone_number_collection={'enabled': True}, # Option
                shipping_address_collection={'allowed_countries': ['US']}, # Option
                success_url=settings.MYSITE_DOMAIN + '/success/',
            )
        except Exception as e:
            return str(e)
        # 2-3. Direct to payment page
        return redirect(checkout_session.url)


class SuccessView(TemplateView):
    template_name = "core/success.html"
