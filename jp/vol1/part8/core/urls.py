from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('item/<int:pk>/', ItemView.as_view(), name='item'), # pkは商品のpk
    path('cart/<int:pk>/', CartView.as_view(), name='cart'), # pkはユーザーのpk
    path('delete_cart_item/<int:pk>/', DeleteCartItemView.as_view(), name='delete_cart_item'),  # pkはユーザーのpk
    path('order/', OrderView.as_view(), name='order'),
    path('success/', SuccessView.as_view(), name='success'),
]
