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
    以下いずれかの場合のみアクセスを許可するMixinです。
    
    'ユーザーのpkがURLのpkと一致する' or 'ユーザーがスーパーユーザーである'
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


class OrderView(View):
    def post(self, *args, **kwargs):
        """
        '購入へ進む'ボタンが押された時(=POSTリクエストが送信された時)
        Orderオブジェクトを作ると同時にユーザーのカートを空にします。
        [手順]
        1. Orderオブジェクトを作成
        2. カートの中身(cart_items)をOrderオブジェクトのorder_itemsにコピー
        3. カートの中身をリセット
        4. 決済ページにリダイレクト
        """
        # 1. Orderオブジェクトを作成
        order_user = self.request.user
        order_cart = order_user.cart
        order_obj = Order.objects.create(
            user=order_user,
            order_price=order_cart.total_price,
        )
        # 2. カートの中身(cart_items)をOrderオブジェクトのorder_itemsにコピー
        # 右記のようにも記述できます: order_obj.order_items.add(*order_cart.cart_items.all())
        for cart_item in order_cart.cart_items.all():
            order_obj.order_items.add(cart_item)
        # 3. カートの中身をリセット
        order_cart.cart_items.clear()
        # 4. 決済ページにリダイレクト
        # のちの実装でリダイレクト先を外部決済ページとしますが、一旦successページとしておきます
        return redirect(reverse_lazy('success'))


class SuccessView(TemplateView):
    template_name = "core/success.html"
