import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from learning_hub.models import Category, Certification, Course, Formation, Institution


@pytest.fixture
def sample_data(db):
    institution = Institution.objects.create(name="Tech Academy")
    category = Category.objects.create(name="Tech")
    formation = Formation.objects.create(
        name="AI Specialist",
        workload=120,
        start_date=timezone.now().date(),
    )
    course = Course.objects.create(
        name="Machine Learning Bootcamp",
        workload=60,
        institution=institution,
        start_date=timezone.now().date(),
        is_active=True,
    )
    certification = Certification.objects.create(
        name="ML Professional",
        institution=institution,
        issue_date=timezone.now().date(),
        is_active=True,
    )
    return {
        "institution": institution,
        "category": category,
        "formation": formation,
        "course": course,
        "certification": certification,
    }


@pytest.mark.django_db
class TestContentProtection:
    """Verify that unauthenticated users are redirected to login for all content views."""

    def test_unauthenticated_index_redirects_to_login(self, client):
        response = client.get(reverse("index"))
        assert response.status_code == 302
        assert response.url == f"{reverse('accounts:login')}?next=/"

    def test_unauthenticated_formations_redirects_to_login(self, client):
        response = client.get(reverse("formations"))
        assert response.status_code == 302
        assert response.url == f"{reverse('accounts:login')}?next=/formations/"

    def test_unauthenticated_courses_redirects_to_login(self, client):
        response = client.get(reverse("courses"))
        assert response.status_code == 302
        assert response.url == f"{reverse('accounts:login')}?next=/courses/"

    def test_unauthenticated_course_detail_redirects_to_login(self, client, sample_data):
        url = reverse("course", kwargs={"pk": sample_data["course"].pk})
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == f"{reverse('accounts:login')}?next={url}"

    def test_unauthenticated_certifications_redirects_to_login(self, client):
        response = client.get(reverse("certifications"))
        assert response.status_code == 302
        assert response.url == f"{reverse('accounts:login')}?next=/certifications/"

    def test_unauthenticated_certification_detail_redirects_to_login(self, client, sample_data):
        url = reverse("certification", kwargs={"pk": sample_data["certification"].pk})
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == f"{reverse('accounts:login')}?next={url}"

    def test_authenticated_user_accesses_content(self, authenticated_client, sample_data):
        """Logged-in users have full access to all pages."""
        urls = [
            reverse("index"),
            reverse("formations"),
            reverse("courses"),
            reverse("course", kwargs={"pk": sample_data["course"].pk}),
            reverse("certifications"),
            reverse("certification", kwargs={"pk": sample_data["certification"].pk}),
        ]
        for url in urls:
            response = authenticated_client.get(url)
            assert response.status_code == 200


@pytest.mark.django_db
class TestApiCompatibility:
    """Verify that stevillis.com.br communication via API & JWT is not broken."""

    def test_api_courses_not_redirected_to_html_login(self, db):
        api_client = APIClient()
        # Unauthenticated request to DRF endpoint returns 401 JSON, NOT a 302 redirect
        response = api_client.get(reverse("api_courses"))
        assert response.status_code == 401
        assert response.headers["Content-Type"] == "application/json"

    def test_api_certifications_not_redirected_to_html_login(self, db):
        api_client = APIClient()
        response = api_client.get(reverse("api_certifications"))
        assert response.status_code == 401
        assert response.headers["Content-Type"] == "application/json"

    def test_api_courses_with_jwt_admin_succeeds(self, db, admin_user, sample_data):
        api_client = APIClient()
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("api_courses"))
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
        assert len(data["courses"]) == 1
        assert data["courses"][0]["name"] == "Machine Learning Bootcamp"

    def test_api_certifications_with_jwt_admin_succeeds(self, db, admin_user, sample_data):
        api_client = APIClient()
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("api_certifications"))
        assert response.status_code == 200
        data = response.json()
        assert "certifications" in data
        assert len(data["certifications"]) == 1
        assert data["certifications"][0]["name"] == "ML Professional"
