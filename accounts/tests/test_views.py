import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAccountsViews:
    def test_login_view_get(self, client):
        url = reverse("accounts:login")
        response = client.get(url)
        assert response.status_code == 200
        assert "accounts/login.html" in [t.name for t in response.templates]

    def test_unauthenticated_login_page_has_no_menu_or_sensitive_info(self, client):
        """Ensure no navigation options, external links, or sensitive data are exposed to anonymous visitors."""
        url = reverse("accounts:login")
        response = client.get(url)
        content = response.content.decode("utf-8")

        # Verify no navigation links or options are displayed
        assert reverse("courses") not in content
        assert reverse("formations") not in content
        assert reverse("certifications") not in content
        assert "mobile-menu" not in content
        assert "mobile-menu-button" not in content
        assert "https://github.com" not in content
        assert "https://www.linkedin.com" not in content
        assert "Portfólio" not in content

        # Verify login form is present
        assert 'name="username"' in content
        assert 'name="password"' in content
        assert "Entrar" in content

    def test_login_view_authenticated_redirect(self, authenticated_client):
        url = reverse("accounts:login")
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url == "/"

    def test_login_view_post_success(self, client, user):
        url = reverse("accounts:login")
        response = client.post(
            url,
            {"username": "testuser", "password": "password123"},
        )
        assert response.status_code == 302
        assert response.url == "/"

    def test_login_view_post_success_with_next(self, client, user):
        url = f"{reverse('accounts:login')}?next=/courses/"
        response = client.post(
            url,
            {"username": "testuser", "password": "password123"},
        )
        assert response.status_code == 302
        assert response.url == "/courses/"

    def test_login_view_post_invalid(self, client, user):
        url = reverse("accounts:login")
        response = client.post(
            url,
            {"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_logout_view_post(self, authenticated_client):
        url = reverse("accounts:logout")
        response = authenticated_client.post(url)
        assert response.status_code == 302
        assert response.url == "/"

    def test_logout_view_get_authenticated(self, authenticated_client):
        url = reverse("accounts:logout")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "accounts/logout_confirm.html" in [t.name for t in response.templates]

    def test_logout_view_get_unauthenticated(self, client):
        url = reverse("accounts:logout")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse("accounts:login")
