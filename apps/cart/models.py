from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from apps.products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), Decimal('0')) # type: ignore

    def __str__(self):
        return f'Cart of {self.user}'

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name = 'unique_product_per_cart'
            )
        ]

    @property
    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.quantity} x {self.product}'
    