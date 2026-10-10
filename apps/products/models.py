from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal

from .validators import validate_image_entenstion, validate_image_size

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=275)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        '''Slugify the title'''
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=275)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, # keep the Product
        related_name='products',
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_entenstion],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # newests first

    def save(self, *args, **kwargs):
        '''Slugify the title into a unique slug (may add numbers at the end)'''
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 2
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base}-{counter}'
                counter += 2
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name