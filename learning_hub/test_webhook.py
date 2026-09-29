import hashlib
import hmac
from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import AdminSite
from django.test import TestCase, override_settings
from django.utils import timezone

from learning_hub.admin import CourseAdmin, sync_selected_to_rag
from learning_hub.models import Category, Certification, Course, Institution
from learning_hub.services.webhook_service import build_payload, dispatch_webhook, send_webhook


class TestWebhookService(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name="Alura")
        self.category = Category.objects.create(name="Python")
        self.course = Course.objects.create(
            name="Django Masterclass",
            workload=40.0,
            description="Deep dive into Django",
            curriculum_map="Module 1, Module 2",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            institution=self.institution,
            is_active=True,
        )
        self.course.categories.add(self.category)

        self.certification = Certification.objects.create(
            name="AWS Certified Developer",
            workload=60.0,
            description="Associate certification",
            credential_url="https://aws.amazon.com/verify/123",
            credential_id="AWS-12345",
            issue_date=timezone.now().date(),
            institution=self.institution,
            is_active=True,
        )

    def test_build_payload_course(self):
        payload = build_payload(self.course, action="upsert")
        assert payload["event"] == "course.upsert"
        assert payload["model"] == "course"
        assert payload["action"] == "upsert"
        assert payload["data"]["name"] == "Django Masterclass"
        assert payload["data"]["institution"] == "Alura"
        assert payload["data"]["is_active"] is True
        assert "course/" in payload["data"]["url"]

    def test_build_payload_certification(self):
        payload = build_payload(self.certification, action="upsert")
        assert payload["event"] == "certification.upsert"
        assert payload["model"] == "certification"
        assert payload["data"]["name"] == "AWS Certified Developer"
        assert payload["data"]["credential_id"] == "AWS-12345"
        assert "certification/" in payload["data"]["url"]

    def test_send_webhook_unconfigured(self):
        with override_settings(STEVILLIS_WEBHOOK_URL="", STEVILLIS_WEBHOOK_SECRET=""):
            result = send_webhook({"test": "data"})
            assert result is False

    @patch("learning_hub.services.webhook_service.requests.post")
    def test_send_webhook_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with override_settings(
            STEVILLIS_WEBHOOK_URL="https://stevillis.com.br/api/webhooks/learning-hub/",
            STEVILLIS_WEBHOOK_SECRET="super-secret-key",
        ):
            payload = build_payload(self.course, action="upsert")
            result = send_webhook(payload)
            assert result is True

            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "https://stevillis.com.br/api/webhooks/learning-hub/"

            # Verify signature header
            headers = kwargs["headers"]
            assert "X-Webhook-Signature-256" in headers
            sig_header = headers["X-Webhook-Signature-256"]
            assert sig_header.startswith("sha256=")

            expected_sig = (
                "sha256="
                + hmac.new(
                    b"super-secret-key",
                    kwargs["data"],
                    hashlib.sha256,
                ).hexdigest()
            )
            assert sig_header == expected_sig

    @patch("learning_hub.services.webhook_service.requests.post")
    def test_send_webhook_network_error(self, mock_post):
        import requests

        mock_post.side_effect = requests.RequestException("Connection refused")

        with override_settings(
            STEVILLIS_WEBHOOK_URL="https://stevillis.com.br/api/webhooks/learning-hub/",
            STEVILLIS_WEBHOOK_SECRET="super-secret-key",
        ):
            payload = build_payload(self.course, action="upsert")
            result = send_webhook(payload)
            assert result is False

    @patch("learning_hub.services.webhook_service.send_webhook")
    def test_dispatch_webhook_sync(self, mock_send):
        payload = {"event": "test"}
        dispatch_webhook(payload, async_mode=False)
        mock_send.assert_called_once_with(payload)


class TestWebhookSignals(TestCase):
    @patch("learning_hub.signals.dispatch_webhook")
    def test_course_save_triggers_webhook(self, mock_dispatch):
        with self.captureOnCommitCallbacks(execute=True):
            Course.objects.create(
                name="New Course",
                workload=10,
                start_date=timezone.now().date(),
                is_active=True,
            )
        assert mock_dispatch.called

        payload = mock_dispatch.call_args[0][0]
        assert payload["event"] == "course.upsert"
        assert payload["data"]["name"] == "New Course"

    @patch("learning_hub.signals.dispatch_webhook")
    def test_course_inactive_triggers_delete_webhook(self, mock_dispatch):
        with self.captureOnCommitCallbacks(execute=True):
            Course.objects.create(
                name="Inactive Course",
                workload=10,
                start_date=timezone.now().date(),
                is_active=False,
            )
        assert mock_dispatch.called
        payload = mock_dispatch.call_args[0][0]
        assert payload["event"] == "course.delete"

    @patch("learning_hub.signals.dispatch_webhook")
    def test_certification_save_triggers_webhook(self, mock_dispatch):
        with self.captureOnCommitCallbacks(execute=True):
            Certification.objects.create(
                name="New Cert",
                issue_date=timezone.now().date(),
                is_active=True,
            )
        assert mock_dispatch.called
        payload = mock_dispatch.call_args[0][0]
        assert payload["event"] == "certification.upsert"
        assert payload["data"]["name"] == "New Cert"

    @patch("learning_hub.signals.dispatch_webhook")
    def test_course_delete_triggers_webhook(self, mock_dispatch):
        course = Course.objects.create(
            name="To Delete",
            workload=10,
            start_date=timezone.now().date(),
            is_active=True,
        )
        with self.captureOnCommitCallbacks(execute=True):
            course.delete()
        assert mock_dispatch.called
        payload = mock_dispatch.call_args[0][0]
        assert payload["event"] == "course.delete"


class TestAdminSyncAction(TestCase):
    @patch("learning_hub.admin.send_webhook")
    def test_sync_selected_to_rag(self, mock_send):
        mock_send.return_value = True
        course = Course.objects.create(
            name="Admin Sync Course",
            workload=20,
            start_date=timezone.now().date(),
            is_active=True,
        )
        request = MagicMock()
        admin = CourseAdmin(Course, AdminSite())

        sync_selected_to_rag(admin, request, Course.objects.filter(pk=course.pk))
        assert mock_send.called
        payload = mock_send.call_args[0][0]
        assert payload["data"]["name"] == "Admin Sync Course"
