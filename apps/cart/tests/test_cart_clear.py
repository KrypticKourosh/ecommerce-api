# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from .factories import CartFactory, CartItemFactory


@pytest.mark.django_db
class TestCartClear:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('cart')
        self.user = UserFactory()
        self.cart = CartFactory(user=self.user)
        CartItemFactory(cart=self.cart)
        CartItemFactory(cart=self.cart)

    def test_anonymous_cannot_clear_cart(self):
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert self.cart.items.count() == 2

    def test_clear_removes_all_items(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert self.cart.items.count() == 0
