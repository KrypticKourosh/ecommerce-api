# type: ignore 
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import UserFactory

@pytest.mark.django_db
class TestProfile:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('profile')
        self.user = UserFactory()

    def test_anonymous_user_cannot_get_profile(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_cannot_get_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == self.user.email 

    def test_user_can_update_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {'first_name': 'John'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name']        
        self.user.refresh_from_db()
        assert self.user.first_name == 'John'

    def test_email_is_read_only(self):
        self.client.force_authenticate(user=self.user)
        old_email = self.user.email
        response = self.client.patch(self.url, {'email': 'newemail@example.com'})
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.email == old_email