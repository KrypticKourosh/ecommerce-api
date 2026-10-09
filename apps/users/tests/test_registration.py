# type: ignore 
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import UserFactory

@pytest.mark.django_db
class TestRegistration:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('register')
        self.data = {
            'email': 'newuser@example.com',
            'password': 'string1234',
            'password2': 'string1234',
        }

    def register(self, **overrides):
        return self.client.post(self.url, {**self.data, **overrides})

    def test_user_can_register(self):
        response = self.register()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newuser@example.com'
        assert 'password' not in response.data

    def test_password_must_match(self):
        response = self.register(password2='different1234')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_register_duplicate_email(self):
        UserFactory(email=self.data['email'])
        response = self.register()
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_email_check_ignores_case(self):
        UserFactory(email=self.data['email'])
        response = self.register(email='nEwuSeR@eXamPle.cOM')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_is_rejected(self):
        response = self.register(password='pass', password2='pass')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
