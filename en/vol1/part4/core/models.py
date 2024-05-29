from django.conf import settings
from django.db import models

# Create your models here.
"""
=====================================
 3 Types of How to Import User Model
=====================================

1. From settings.py file
--------------------------------
from django.conf import settings
User = settings.AUTH_USER_MODEL

2. By get_user_model function
--------------------------------
from django.contrib.auth import get_user_model
User = get_user_model()

3. Import directly
--------------------------------
from accounts.models import CustomUser

"""
User = settings.AUTH_USER_MODEL


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)


class CartItem(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Cart(models.Model):
    cart_items = models.ManyToManyField(to=CartItem, blank=True)    # In ManyToManyField, null=True is meaningless. If set, the following warning occurs:
                                                                    # core.Cart.cart_items: (fields.W340) null has no effect on ManyToManyField.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # If you want to keep order history when user is deleted, SET_NULL instead of CASCADE.
    order_items = models.ManyToManyField(to=CartItem, blank=True)
    order_price = models.FloatField()
    ordered_date = models.DateTimeField(auto_now=True)