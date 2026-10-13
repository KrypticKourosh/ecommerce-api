# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from .factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
class TestCategoryRead:
    def setup_method(self):
        self.client = APIClient()
        self.category = CategoryFactory()

    def test_anonymous_can_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


    def test_anonymous_can_retrieve_category_by_slug(self):
        url = reverse('category-detail', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == self.category.name

@pytest.mark.django_db
class TestCategoryWrite:
    def setup_method(self):
        self.client = APIClient()
        self.category = CategoryFactory()
        self.url = reverse('category-list')
        self.data = {
            'name': 'shoes',
            'description': 'All kind of shoes'
        }
        self.staff = UserFactory(is_staff=True)

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

    def test_slug_in_request_is_ignored(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(self.url, {**self.data, 'slug': 'custom-slug'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['slug'] == 'shoes'

    def test_reject_duplicate_name(self):
        self.client.force_authenticate(user=self.staff)
        CategoryFactory(name='shoes') # lower case s
        response = self.client.post(self.url, {'name': 'Shoes'}) # upper case s
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_staff_can_update(self):
        self.client.force_authenticate(user=self.staff)
        url = reverse('category-detail', kwargs={'slug': self.category.slug}) 
        response = self.client.patch(url, {'description': 'updated'})
        assert response.status_code == status.HTTP_200_OK
        self.category.refresh_from_db()
        assert self.category.description == 'updated'

    def test_renaming_does_not_change_slug(self):
        self.client.force_authenticate(user=self.staff)
        old_slug = self.category.slug
        url = reverse('category-detail', kwargs={'slug': old_slug}) 
        response = self.client.patch(url, {'name': 'updated'})
        assert response.status_code == status.HTTP_200_OK
        self.category.refresh_from_db()
        assert self.category.slug == old_slug 

@pytest.mark.django_db
class TestCategoryDelete:
    def setup_method(self):
        self.client = APIClient()
        self.staff = UserFactory(is_staff=True)
        self.category = CategoryFactory()
        self.url = reverse('category-detail', kwargs={'slug': self.category.slug})

    def test_staff_can_delete_empty_category(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cannot_delete_category_with_products(self):
        ProductFactory(category=self.category)
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_409_CONFLICT
