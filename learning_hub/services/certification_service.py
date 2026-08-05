"""Service functions for Certification model operations."""

from django.db.models import QuerySet
from django.http import Http404

from learning_hub.models import Certification


def get_certification(pk: int) -> Certification:
    """
    Fetches a single certification by its primary key.
    Raises Http404 if not found.
    """
    try:
        return Certification.objects.get(pk=pk)
    except Certification.DoesNotExist:
        raise Http404("Certification not found!")


def get_certifications() -> QuerySet:
    """
    Fetches all active certifications, ordered by issue date descending.
    """
    return Certification.objects.filter(is_active=True).order_by("-issue_date")
