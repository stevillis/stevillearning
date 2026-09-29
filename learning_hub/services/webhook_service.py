"""
Service to build and dispatch webhooks to stevillis.com.br when courses,
or certifications are created, updated, or deleted.
"""

import hashlib
import hmac
import json
import logging
import threading
import time

import requests
from django.conf import settings
from django.urls import NoReverseMatch, reverse

logger = logging.getLogger(__name__)


def build_payload(
    instance,
    action: str,
    site_base_url: str = "https://learning.stevillis.com.br",
    instance_id: int | None = None,
) -> dict:
    """Build a standardized webhook payload for Course or Certification.

    Args:
        instance: The model instance (Course, Certification).
        action: Either 'upsert' or 'delete'.
        site_base_url: Base domain for constructing absolute URLs.
        instance_id: Optional ID to preserve ID during post_delete.

    Returns:
        A dict matching the standardized webhook schema.
    """
    model_name = instance._meta.model_name  # 'course', 'certification'
    item_id = instance_id if instance_id is not None else instance.pk

    if action == "delete":
        return {
            "event": f"{model_name}.delete",
            "model": model_name,
            "action": "delete",
            "data": {
                "id": item_id,
                "name": getattr(instance, "name", ""),
            },
        }

    data = {
        "id": item_id,
        "name": getattr(instance, "name", ""),
        "workload": getattr(instance, "workload", None),
        "description": getattr(instance, "description", "") or "",
        "start_date": (str(instance.start_date) if getattr(instance, "start_date", None) else None),
        "end_date": str(instance.end_date) if getattr(instance, "end_date", None) else None,
        "is_active": getattr(instance, "is_active", True),
    }

    if hasattr(instance, "institution") and instance.institution:
        data["institution"] = str(instance.institution)

    if model_name == "course":
        data["curriculum_map"] = getattr(instance, "curriculum_map", "") or ""
        try:
            rel_url = reverse("course", args=[instance.pk])
            data["url"] = f"{site_base_url.rstrip('/')}{rel_url}"
        except NoReverseMatch:
            data["url"] = f"{site_base_url.rstrip('/')}/course/{instance.pk}"
        if hasattr(instance, "categories"):
            data["categories"] = [c.name for c in instance.categories.all()]

    elif model_name == "certification":
        data["credential_url"] = getattr(instance, "credential_url", "") or ""
        data["credential_id"] = getattr(instance, "credential_id", "") or ""
        data["issue_date"] = (
            str(instance.issue_date) if getattr(instance, "issue_date", None) else None
        )
        data["expiration_date"] = (
            str(instance.expiration_date) if getattr(instance, "expiration_date", None) else None
        )
        try:
            rel_url = reverse("certification", args=[instance.pk])
            data["url"] = f"{site_base_url.rstrip('/')}{rel_url}"
        except NoReverseMatch:
            data["url"] = f"{site_base_url.rstrip('/')}/certification/{instance.pk}"
        if hasattr(instance, "categories"):
            data["categories"] = [c.name for c in instance.categories.all()]

    return {
        "event": f"{model_name}.{action}",
        "model": model_name,
        "action": action,
        "data": data,
    }


def send_webhook(payload: dict) -> bool:
    """Send webhook HTTP POST request to configured STEVILLIS_WEBHOOK_URL.

    Uses HMAC-SHA256 signature and shared secret header.

    Returns:
        True if delivery succeeded (HTTP 200/201), False otherwise.
    """
    webhook_url = getattr(settings, "STEVILLIS_WEBHOOK_URL", "")
    webhook_secret = getattr(settings, "STEVILLIS_WEBHOOK_SECRET", "")

    if not webhook_url or not webhook_secret:
        logger.debug(
            "STEVILLIS_WEBHOOK_URL or STEVILLIS_WEBHOOK_SECRET not configured. Skipping webhook."
        )
        return False

    body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    signature = hmac.new(
        webhook_secret.encode("utf-8"),
        body_bytes,
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature-256": f"sha256={signature}",
        "X-Webhook-Timestamp": str(int(time.time())),
        "X-Webhook-Secret": webhook_secret,
        "User-Agent": "StevillisLearning-Webhook/1.0",
    }

    try:
        response = requests.post(
            webhook_url,
            data=body_bytes,
            headers=headers,
            timeout=10,
        )
        if response.status_code in (200, 201):
            logger.info(
                "Successfully delivered webhook %s to %s",
                payload.get("event"),
                webhook_url,
            )
            return True
        logger.warning("Webhook delivery failed (%s): %s", response.status_code, response.text)
        return False
    except requests.RequestException as e:
        logger.error("Error dispatching webhook to %s: %s", webhook_url, e)
        return False


def dispatch_webhook(payload: dict, async_mode: bool = True) -> None:
    """Dispatch the webhook payload.

    Args:
        payload: Dict to send.
        async_mode: If True, executes in a background daemon thread so it
            never blocks request handling.
    """
    if async_mode:
        thread = threading.Thread(target=send_webhook, args=(payload,), daemon=True)
        thread.start()
    else:
        send_webhook(payload)
