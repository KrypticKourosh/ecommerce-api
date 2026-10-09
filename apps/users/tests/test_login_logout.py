# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory, DEFAULT_PASSWORD

@pytest.mark.django_db
class TestLogin:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('token-obtain-pair')
        self.user = UserFactory()
        self.data = {
            'email': self.user.email,
            'password': DEFAULT_PASSWORD,
        }

    def login(self, **overrides):
        return self.client.post(self.url, {**self.data, **overrides})
        
    def test_user_can_login_with_email(self):
        response = self.login()
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_unregistered_email_fails(self):
        response = self.login(email='UnregisteredUser@example.com')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_password_fails(self):
        response = self.login(password='wrongpassword')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED



@pytest.mark.django_db
class TestLogout:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('token-blacklist')
        self.user = UserFactory()

    def logout(self, refresh):
        return self.client.post(self.url, {'refresh': refresh})

    def test_logout_blacklists_refresh_token(self):
        refresh = str(RefreshToken.for_user(self.user))

        #logout
        response = self.logout(refresh)
        assert response.status_code == status.HTTP_200_OK

        # check if refresh token is blacklisted
        response = self.client.post(reverse('token-refresh'), {'refresh': refresh})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_fails(self):
        response = self.logout('invalid-token')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_token_fails(self):
        response = self.client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        