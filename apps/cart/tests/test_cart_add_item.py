# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.cart.models import CartItem
from apps.products.tests.factories import ProductFactory
from apps.users.tests.factories import UserFactory
from .factories import CartFactory, CartItemFactory

PRODUCT_STOCK = 5

@pytest.mark.django_db
class TestAddCartItem:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('cart-item-add')
        self.user = UserFactory()
        self.product = ProductFactory(stock=PRODUCT_STOCK)
        self.client.force_authenticate(user=self.user)  # logged in by default
        self.data = {
            'product_id': self.product.id,
            'quantity': 1,
        }

    def add_item(self, **overrides):
        return self.client.post(self.url, {**self.data, **overrides})

    def test_anonymous_cannot_add_item(self):
        self.client.force_authenticate(user=None)
        response = self.add_item()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_product_to_cart(self):
        response = self.add_item(quantity=1)
        assert response.status_code == status.HTTP_201_CREATED
        item = CartItem.objects.get(cart__user=self.user)
        assert item.product == self.product
        assert item.quantity == 1

    def test_quantity_defaults_to_one(self):
        response = self.client.post(self.url, {'product_id': self.product.id}) # no quantity
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.get(cart__user=self.user).quantity == 1

    def test_adding_same_product_increases_quantity(self):
        self.add_item(quantity=2)
        self.add_item(quantity=1)
        items = CartItem.objects.filter(cart__user=self.user)
        assert items.count() == 1 # no dup records
        assert items.first().quantity == 3

    def test_quantity_above_stock_is_rejected(self):
        response = self.add_item(product_id=self.product.id, quantity=PRODUCT_STOCK + 1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'quantity' in response.data

    def test_stock_check_counts_items_already_in_cart(self):
        cart = CartFactory(user=self.user)
        item = CartItemFactory(cart=cart, product=self.product, quantity=3)
        response = self.add_item(product_id=self.product.id, quantity=3)  # 3 + 3 > 5
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        item.refresh_from_db()
        assert item.quantity == 3

    def test_inactive_product_is_rejected(self):
        inactive = ProductFactory(is_active=False, stock=5)
        response = self.add_item(product_id=inactive.id, quantity=1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not CartItem.objects.filter(cart__user=self.user).exists()