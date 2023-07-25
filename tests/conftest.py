import pytest
from django.contrib.auth.models import AbstractUser, User
from rest_framework.test import APIClient


@pytest.fixture
def superuser() -> AbstractUser:
    """
    Creates a superuser.
    """
    return User.objects.create_superuser("admin", "admin@example.com", "dummy_password")


@pytest.fixture
def user() -> AbstractUser:
    """
    Creates a normal user.
    """
    return User.objects.create_user("user", "user@example.com", "dummy_password")


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def authorized_api_client(api_client: APIClient, user: User) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture()
def authorized_api_client(api_client: APIClient, user: User) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client
