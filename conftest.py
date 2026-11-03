import pytest
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    """Use fast MD5 password hasher during tests to speed up execution."""
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]


@pytest.fixture
def user(db):
    """Creates a standard test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="password123",
    )


@pytest.fixture
def admin_user(db):
    """Creates an admin test user."""
    return User.objects.create_superuser(
        username="adminuser",
        email="admin@example.com",
        password="adminpassword123",
    )


@pytest.fixture
def authenticated_client(client, user):
    """Returns a test client logged in as regular user."""
    client.login(username="testuser", password="password123")
    return client
