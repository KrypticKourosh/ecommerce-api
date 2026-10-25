# type: ignore
import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory
from .factories import CartFactory, CartItemFactory


@pytest.mark.django_db
class TestCartView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('cart')
        self.user = UserFactory()

    def test_anonymous_cannot_view_cart(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_can_create_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.data
        assert Decimal(response.data['total']) == Decimal('0')

    def test_cart_shows_items_and_total(self):
        cart = CartFactory(user=self.user)
        # different products to check subtotal and total
        shoes = ProductFactory(name='shoes', price=Decimal('100'))
        pencil = ProductFactory(name='pencil', price=Decimal('2'))
        CartItemFactory(cart=cart, product=shoes, quantity=2)
        CartItemFactory(cart=cart, product=pencil, quantity=3)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        
        # details:
        # total
        assert response.data['total'] == Decimal('206') # 2 * 100 + 3 * 2
        # subtotoal
        shoes_response = response.data['items'][0]
        assert shoes_response['subtotal'] == Decimal('200')
        # quantity check
        assert shoes_response['quantity'] == 2