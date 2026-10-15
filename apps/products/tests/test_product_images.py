# type: ignore
import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from .factories import CategoryFactory

def make_image(name='product.png'):
    '''Test image'''
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')

@pytest.fixture(autouse=True)
def temp_media(settings, tmp_path):
    '''Test media path'''
    settings.MEDIA_ROOT = tmp_path

@pytest.mark.django_db
class TestProductImage:
    def setup_method(self):
        self.client = APIClient()
        self.client.force_authenticate(user=UserFactory(is_staff=True))
        self.url = reverse('product-list')
        self.data = {
            'name': 'Sneakers',
            'category_id': CategoryFactory().id,
            'price': '59.99',
            'stock': 5,
        }

    def upload(self, image):
        return self.client.post(self.url, {**self.data, 'image': image}, format='multipart')

    def test_staff_can_upload_image(self):
        response = self.upload(make_image())
        assert response.status_code == status.HTTP_201_CREATED
        assert '/media/products' in response.data['image']
        
    def test_reject_unsupported_extension(self):
        response = self.upload(make_image(name='invalid.abc'))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_oversized_image(self, monkeypatch):
        monkeypatch.setattr('apps.products.validators.MAX_IMAGE_SIZE_MB', 0)
        response = self.upload(make_image())
        assert response.status_code == status.HTTP_400_BAD_REQUEST