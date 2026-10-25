from django.urls import path
from .views import CartView, AddCartItemView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('items/', AddCartItemView.as_view(), name='cart-item-add'),
]