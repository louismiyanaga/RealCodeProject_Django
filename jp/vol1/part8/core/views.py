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
    以下いずれかの場合のみアクセスを許可するMixinです。
    
    'ユーザーのpkがURLのpkと一致する' or 'ユーザーがスーパーユーザーである'
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
        デフォルトでListViewが持っているget_context_dataメソッドを編集し、
        テンプレート側で{{form}}が使えるようにオーバーライドします。
        """
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm
        return context
    
    def get_queryset(self):
        """
        デフォルトでListViewが持っているget_querysetメソッドを編集し、
        特定のカテゴリに一致する商品群のみを返すようオーバーライドします。
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
        ユーザー専用のカートページURL(/cart/user_pk/)を取得するメソッドです。
        """
        user_pk = self.request.user.id
        return reverse_lazy('cart', kwargs={'pk': user_pk}) # kwargsの部分は args=(user_pk,) としてもOK
    
    def post(self, *args, **kwargs):
        """
        'カートに追加'ボタンが押された時(=POSTリクエストが送信された時)
        カートアイテム(商品と購入数)をカートに追加するためのメソッドです。
        DetailViewはpostメソッドを持っていないので、新たに作成します。
        [手順]
        1. HTMLのformから商品のpkとquantityの情報を取得
        2. 取得した情報をもとにカートアイテムを作成
        3. 作成したカートアイテムをユーザーのカートに追加
        4. カートページにリダイレクト
        """
        # 1. HTMLのformから商品のpkとquantityの情報を取得
        item_pk = self.request.POST.get('item_pk')
        quantity = int(self.request.POST.get('quantity'))
        # 2. 取得した情報をもとにカートアイテムを作成
        item = Item.objects.get(id=item_pk)
        cart_item = CartItem(item=item, quantity=quantity)
        # 3. 作成したカートアイテムをユーザーのカートに追加
        user = self.request.user
        user.cart.add_cart_item(cart_item)
        # 4. カートページにリダイレクト
        return redirect(self.get_success_url())


class CartView(LoginRequiredMixin, OnlyYouMixin, DetailView):
    template_name = "core/cart.html"
    model = User
    context_object_name = 'cart'

    def get_object(self, queryset=None):
        """
        デフォルトでDetailViewが持っているget_objectメソッドを編集します。
        modelにユーザーモデルを指定しているので、このままではテンプレートから
        取得されるオブジェクトはユーザーオブジェクトになります。
        カートオブジェクトを取り出せるように、以下の通りオーバーライドします。
        """
        user = super().get_object(queryset)
        return user.cart


class DeleteCartItemView(LoginRequiredMixin, OnlyYouMixin, DeleteView):
    model = User

    def get_object(self, queryset=None):
        """
        デフォルトでDeleteViewが持っているget_objectメソッドを編集します。
        modelにユーザーモデルを指定しているので、このままでは削除対象となる
        オブジェクトはユーザーになります。
        ユーザーではなく、カートに入っている"特定のカートアイテム"を削除対象
        とするよう、以下の通りオーバーライドします。
        [手順]
        1. formからカートアイテムのpkを取得
        2. カートの中から、取得したpkと一致するカートアイテムを取得
        """
        user = super().get_object(queryset)
        # 1. formからカートアイテムのpkを取得
        cart_item_pk = self.request.POST['cart_item_pk']
        # 2. カートの中から、取得したpkと一致するカートアイテムを取得
        cart_item = user.cart.cart_items.get(id=cart_item_pk)
        return cart_item
    
    def get_success_url(self):
        """
        ユーザー専用のカートページURL(/cart/user_pk/)を取得するメソッドです。
        """
        user_pk = self.request.user.id
        return reverse_lazy('cart', kwargs={'pk': user_pk}) # kwargsの部分は args=(user_pk,) としてもOK


class OrderView(View):
    def post(self, *args, **kwargs):
        """
        '購入へ進む'ボタンが押された時(=POSTリクエストが送信された時)
        大きく分けて以下の２つの処理が実行されるメソッドです。

        1. Django側の処理
        2. Stripe決済処理
        
        """
        
        """
        --------------------------------------------------------------
        1. Django側の処理
        --------------------------------------------------------------
        
        Orderオブジェクトを作ると同時にユーザーのカートを空にします。
        [手順]
        1-1. Orderオブジェクトを作成
        1-2. カートの中身(cart_items)をOrderオブジェクトのorder_itemsにコピー
        1-3. カートの中身をリセット
        """
        # 1-1. Orderオブジェクトを作成
        order_user = self.request.user
        order_cart = order_user.cart
        order_obj = Order.objects.create(
            user=order_user,
            order_price=order_cart.total_price,
        )
        # 1-2. カートの中身(cart_items)をOrderオブジェクトのorder_itemsにコピー
        # 右記のようにも記述できます: order_obj.order_items.add(*order_cart.cart_items.all())
        for cart_item in order_cart.cart_items.all():
            order_obj.order_items.add(cart_item)
        # 1-3. カートの中身をリセット
        order_cart.cart_items.clear()
        
        """
        --------------------------------------------------------------
        2. Stripe決済処理
        --------------------------------------------------------------
        
        ユーザーをStripeの決済ページにリダイレクトさせます。
        [手順]
        2-1. line_items(購入情報のリスト)を作成
        2-2. checkout_sessionを作成
        2-3. 決済ページにリダイレクト
        """
        # 2-1. line_items(購入情報のリスト)を作成
        line_items = []
        for order_item in order_obj.order_items.all():
            line_item = {
                'price_data': {
                    'currency': 'jpy',
                    'unit_amount': order_item.item.price,
                    'product_data': {
                        'name': order_item.item.name,
                    }
                },
                'quantity': order_item.quantity,
            }
            line_items.append(line_item)
        # 2-2. checkout_sessionを作成
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                phone_number_collection={'enabled': True}, # 任意
                shipping_address_collection={'allowed_countries': ['JP']}, # 任意
                success_url=settings.MYSITE_DOMAIN + '/success/',
            )
        except Exception as e:
            return str(e)
        # 2-3. 決済ページにリダイレクト
        return redirect(checkout_session.url)


class SuccessView(TemplateView):
    template_name = "core/success.html"
