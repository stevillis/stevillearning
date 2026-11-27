import os
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest
from django.db import OperationalError
from django.template.loader import render_to_string
from django.test import Client, RequestFactory, override_settings
from django.urls import reverse
from django.views.defaults import server_error

SETTINGS_PATH = str(Path(__file__).resolve().parent / "settings.py")


def test_500_template_is_self_contained_and_safe():
    """Verify 500.html renders without DB/request context and leaks no internal details."""
    html = render_to_string("500.html")

    assert "Sistema temporariamente indisponível" in html
    assert "Tentar novamente" in html
    assert 'href="/accounts/login/"' in html

    # Must not rely on Django template tags/context or expose internal details
    assert "{%" not in html
    assert "{{" not in html
    assert "Supabase" not in html
    assert "OperationalError" not in html
    assert "/courses/" not in html
    assert "/formations/" not in html
    assert "/certifications/" not in html


def test_default_server_error_handler_uses_custom_500_template():
    """Verify Django's default 500 handler renders our custom 500.html."""
    request = RequestFactory().get("/accounts/login/")
    response = server_error(request)

    assert response.status_code == 500
    content = response.content.decode("utf-8")
    assert "Sistema temporariamente indisponível" in content


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_login_returns_custom_500_when_database_is_unavailable():
    """Simulate database unavailability on login and ensure custom 500 page is returned."""
    client = Client(raise_request_exception=False)
    client.cookies["sessionid"] = "stale-session-id"
    login_url = reverse("accounts:login")

    with patch(
        "django.db.backends.base.base.BaseDatabaseWrapper.cursor",
        side_effect=OperationalError("connection timed out"),
    ):
        response = client.get(login_url)

    assert response.status_code == 500
    content = response.content.decode("utf-8")
    assert "Sistema temporariamente indisponível" in content
    assert "Tentar novamente" in content


def test_settings_sets_connect_timeout_for_postgresql():
    """Verify PostgreSQL receives default/configured connect_timeout without helper functions."""
    with (
        patch("environ.Env.read_env"),
        patch.dict(
            os.environ,
            {"DATABASE_URL": "", "DB_ENGINE": "django.db.backends.postgresql"},
            clear=False,
        ),
    ):
        os.environ.pop("DB_CONNECT_TIMEOUT", None)
        namespace = runpy.run_path(SETTINGS_PATH)

    assert namespace["DATABASES"]["default"]["OPTIONS"]["connect_timeout"] == 5

    with (
        patch("environ.Env.read_env"),
        patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "DB_ENGINE": "django.db.backends.postgresql",
                "DB_CONNECT_TIMEOUT": "12",
            },
            clear=False,
        ),
    ):
        namespace = runpy.run_path(SETTINGS_PATH)

    assert namespace["DATABASES"]["default"]["OPTIONS"]["connect_timeout"] == 12


def test_settings_skips_connect_timeout_for_non_postgresql():
    """Verify non-PostgreSQL backends (such as SQLite) do not receive connect_timeout."""
    with (
        patch("environ.Env.read_env"),
        patch.dict(
            os.environ,
            {"DATABASE_URL": "", "DB_ENGINE": "django.db.backends.sqlite3"},
            clear=False,
        ),
    ):
        namespace = runpy.run_path(SETTINGS_PATH)

    assert "OPTIONS" not in namespace["DATABASES"]["default"]
