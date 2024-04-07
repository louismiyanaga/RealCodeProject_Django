from django.conf import settings
from django.db import models

"""
---------------------------
ユーザーモデルの読み込み方法３種
---------------------------

1. settingsファイルから取得
from django.conf import settings
User = settings.AUTH_USER_MODEL

2. get_user_modelで取得
from django.contrib.auth import get_user_model
User = get_user_model()

3. 直接インポートして取得
from accounts.models import CustomUser

"""

# Create your models here.
User = settings.AUTH_USER_MODEL


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)


class CartItem(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Cart(models.Model):
    cart_items = models.ManyToManyField(to=CartItem, blank=True) # ManyToManyFieldにおいてnull=Trueは無意味のため不要です（右記警告が出ます → core.Cart.cart_items: (fields.W340) null has no effect on ManyToManyField.）


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE) # ユーザーが削除されても注文履歴を残したい場合はon_delete=models.SET_NULLにします
    order_items = models.ManyToManyField(to=CartItem, blank=True)
    order_price = models.PositiveIntegerField()
    ordered_date = models.DateTimeField(auto_now=True)