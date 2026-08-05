import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from mysite.models import Course, Institution


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(django_user_model):
    return django_user_model.objects.create_user(username="testuser", password="testpassword123")


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(
        username="adminuser", password="adminpassword123"
    )


@pytest.mark.django_db
class TestCourseAPI:
    def setup_method(self):
        # Clear cache before each test to reset throttles
        cache.clear()

    def test_courses_unauthenticated_access(self, api_client):
        """Test that unauthenticated access returns 401 Unauthorized."""
        url = reverse("api_courses")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_courses_authenticated_non_admin_access(self, api_client, test_user):
        """Test that authenticated non-admin access returns 403 Forbidden."""
        api_client.force_authenticate(user=test_user)
        url = reverse("api_courses")
        response = api_client.get(url)
        assert response.status_code == 403

    def test_courses_authenticated_admin_access(self, api_client, admin_user):
        """Test that authenticated admin access returns 200 OK."""
        api_client.force_authenticate(user=admin_user)
        url = reverse("api_courses")

        # Create dummy data to verify the endpoint works
        institution = Institution.objects.create(name="Test Institution")
        Course.objects.create(
            name="Test Course",
            workload=40.0,
            institution=institution,
            start_date=timezone.now().date(),
            is_active=True,
        )

        response = api_client.get(url)
        assert response.status_code == 200
        assert "courses" in response.json()
        assert len(response.json()["courses"]) == 1
        assert response.json()["courses"][0]["name"] == "Test Course"

    def test_courses_throttle(self, api_client, admin_user):
        """Test the 100/day user throttle for the courses endpoint."""
        api_client.force_authenticate(user=admin_user)
        url = reverse("api_courses")

        # Make 100 requests (the limit)
        for _ in range(100):
            response = api_client.get(url)
            assert response.status_code == 200

        # The 101st request should be throttled
        response = api_client.get(url)
        assert response.status_code == 429


@pytest.mark.django_db
class TestTokenAPI:
    def setup_method(self):
        # Clear cache before each test to reset throttles
        cache.clear()

    def test_token_throttle(self, api_client):
        """Test the 5/min anon throttle for the token endpoint."""
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "wrongpassword"}

        # Make 5 requests (the limit)
        for _ in range(5):
            response = api_client.post(url, data)
            # Will return 401 because credentials are bad,
            # but throttle evaluates before auth validation for AnonRateThrottle
            assert response.status_code == 401

        # The 6th request should be throttled
        response = api_client.post(url, data)
        assert response.status_code == 429
