"""
Signals for automatically dispatching webhooks to stevillis.com.br
when courses or certifications are updated or deleted.
"""

import logging

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from learning_hub.models import Certification, Course
from learning_hub.services.webhook_service import build_payload, dispatch_webhook

logger = logging.getLogger(__name__)


def _schedule_webhook(instance, action: str):
    """Schedule webhook dispatch after the database transaction commits."""
    instance_id = instance.pk

    def _execute():
        try:
            payload = build_payload(instance, action=action, instance_id=instance_id)
            dispatch_webhook(payload, async_mode=True)
        except Exception:
            logger.exception("Failed to dispatch webhook for %s", instance)

    transaction.on_commit(_execute)


@receiver(post_save, sender=Course)
@receiver(post_save, sender=Certification)
def handle_item_saved(sender, instance, created, **kwargs):
    """Handle creation or update of Course or Certification."""
    if getattr(instance, "is_active", True) is False:
        _schedule_webhook(instance, action="delete")
    else:
        _schedule_webhook(instance, action="upsert")


@receiver(post_delete, sender=Course)
@receiver(post_delete, sender=Certification)
def handle_item_deleted(sender, instance, **kwargs):
    """Handle deletion of Course or Certification."""
    _schedule_webhook(instance, action="delete")


@receiver(m2m_changed, sender=Course.categories.through)
@receiver(m2m_changed, sender=Certification.categories.through)
def handle_m2m_changed(sender, instance, action, **kwargs):
    """Handle M2M relationship changes (e.g. categories added/removed)."""
    if action in ["post_add", "post_remove", "post_clear"] and getattr(instance, "is_active", True):
        _schedule_webhook(instance, action="upsert")
