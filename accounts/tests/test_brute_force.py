import pytest
from axes.models import AccessAttempt
from django.urls import reverse


@pytest.fixture(autouse=True)
def reset_axes_attempts(db):
    """Ensure axes attempt table is clean before and after each test."""
    AccessAttempt.objects.all().delete()
    yield
    AccessAttempt.objects.all().delete()


@pytest.mark.django_db
def test_failed_logins_trigger_lockout(client, user):
    login_url = reverse("accounts:login")

    # Send 4 invalid login attempts (below threshold of 5)
    for _ in range(4):
        response = client.post(
            login_url,
            {"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 200

    # 5th attempt reaches threshold and triggers 429 lockout page
    response = client.post(
        login_url,
        {"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 429
    assert "Muitas Tentativas Incorretas" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_proxy_header_ip_extraction(client, user):
    login_url = reverse("accounts:login")
    client_ip_a = "198.51.100.42"
    client_ip_b = "198.51.100.99"

    # 5 failed attempts from IP A behind proxy (5th triggers lockout)
    for _ in range(5):
        response_a = client.post(
            login_url,
            {"username": "testuser", "password": "wrongpassword"},
            HTTP_X_FORWARDED_FOR=f"{client_ip_a}, 127.0.0.1",
        )

    # IP A is locked out with 429
    assert response_a.status_code == 429

    # Attempt for same user from IP B is NOT locked out
    response_b = client.post(
        login_url,
        {"username": "testuser", "password": "wrongpassword"},
        HTTP_X_FORWARDED_FOR=f"{client_ip_b}, 127.0.0.1",
    )
    assert response_b.status_code == 200


@pytest.mark.django_db
def test_successful_login_resets_failure_count(client, user):
    login_url = reverse("accounts:login")

    # 3 failed attempts
    for _ in range(3):
        client.post(
            login_url,
            {"username": "testuser", "password": "wrongpassword"},
        )

    # 1 successful login
    success_response = client.post(
        login_url,
        {"username": "testuser", "password": "password123"},
    )
    assert success_response.status_code == 302

    # Logout so we can attempt unauthenticated logins again
    client.logout()

    # 4 more failed attempts (total 4 failed since reset, so limit of 5 is not reached)
    for _ in range(4):
        response = client.post(
            login_url,
            {"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 200

    # Verify attempt count is 4, not locked out
    attempt = AccessAttempt.objects.filter(username="testuser").first()
    assert attempt is not None
    assert attempt.failures_since_start == 4
