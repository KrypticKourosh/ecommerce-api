import factory

from apps.cart.models import Cart, CartItem
from apps.users.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory

class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.declarations.SubFactory(UserFactory)

class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.declarations.SubFactory(CartFactory)
    product = factory.declarations.SubFactory(ProductFactory)
    quantity = 1
