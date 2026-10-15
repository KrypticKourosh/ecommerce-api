# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from .factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
class TestProductRead:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('product-list')
        self.category = CategoryFactory()
        self.product = ProductFactory(category=self.category)

    def test_anonymous_can_list_products(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_anonymous_can_retrieve_product_by_slug(self):
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == self.product.name
        assert response.data['category']['name'] == self.category.name

    def test_non_staff_cannot_see_inactive_product(self):
        inactive = ProductFactory(is_active=False)
        response = self.client.get(self.url)
        assert response.data['count'] == 1

        url = reverse('product-detail', kwargs={'slug': inactive.slug})
        assert self.client.get(url).status_code == status.HTTP_404_NOT_FOUND

    def test_staff_can_see_inactive_product(self):
        inactive = ProductFactory(is_active=False)
        staff = UserFactory(is_staff=True)
        self.client.force_authenticate(user=staff)
        response = self.client.get(self.url)
        assert response.data['count'] == 2

        url = reverse('product-detail', kwargs={'slug': inactive.slug})
        assert self.client.get(url).status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductFilter:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('product-list')

    def test_filter_by_category(self):
        catgeory_1 = CategoryFactory()
        catgeory_2 = CategoryFactory()
        ProductFactory(category=catgeory_1)
        ProductFactory(category=catgeory_2)
        response = self.client.get(self.url, {'category': catgeory_1.id})
        assert response.data['count'] == 1
        

@pytest.mark.django_db
class TestProductWrite:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('product-list')
        self.category = CategoryFactory()
        self.staff = UserFactory(is_staff=True)
        self.data = {
            'name': 'Sneakers',
            'category_id': self.category.id,
            'price': '59.99',
            'stock': 5,
        }

    def test_anonymous_cannot_create(self):
        response = self.client.post(self.url, self.data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_staff_cannot_create(self):
        self.client.force_authenticate(user=UserFactory())
        response = self.client.post(self.url, self.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_create(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(self.url, self.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['slug'] == 'sneakers'
        assert response.data['category']['name'] == self.category.name
        assert 'category_id' not in response.data 

    def test_slug_in_request_is_ignored(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(self.url, {**self.data, 'slug': 'custom-slug'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['slug'] == 'sneakers'

    def test_same_name_gets_unique_slug(self):
        ProductFactory(name='Sneakers')
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(self.url, self.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['slug'] == 'sneakers-2'

    def test_category_is_required(self):
        self.client.force_authenticate(user=self.staff)
        del self.data['category_id']
        response = self.client.post(self.url, self.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestProductUpdateDelete:
    def setup_method(self):
        self.client = APIClient()
        self.client.force_authenticate(user=UserFactory(is_staff=True))
        self.product = ProductFactory(name='Sneakers', stock=10)
        self.url = reverse('product-detail', kwargs={'slug': self.product.slug})

    def test_staff_can_update_stock(self):
        response = self.client.patch(self.url, {'stock': 3})
        assert response.status_code == status.HTTP_200_OK
        self.product.refresh_from_db()
        assert self.product.stock == 3

    def test_renaming_does_not_change_slug(self):
        old_slug = self.product.slug
        response = self.client.patch(self.url, {'name': 'New Name'})
        assert response.status_code == status.HTTP_200_OK
        self.product.refresh_from_db()
        assert self.product.slug == old_slug

    def test_non_staff_cannot_update(self):
        self.client.force_authenticate(user=UserFactory())
        response = self.client.patch(self.url, {'stock': 3})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_delete(self):
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT