import factory
from decimal import Decimal

from apps.products.models import Category, Product

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.declarations.Sequence(lambda n: f'Category {n}')
    description = 'a test category'

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.declarations.Sequence(lambda n: f'Product {n}')
    category = factory.declarations.SubFactory(CategoryFactory)
    description = 'a test product'
    price = Decimal('19.99')
    stock = 10
    is_active = True # default