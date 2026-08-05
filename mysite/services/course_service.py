"""Service functions for Course model operations."""

from django.db.models import QuerySet
from django.http import Http404

from mysite.models import Course


def get_course(pk: int) -> tuple[Course, Http404]:
    """
    Fetches a single course by its primary key.
    Raises Http404 if not found.
    """
    try:
        return Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        raise Http404("Course not found!")


def get_courses() -> QuerySet:
    """
    Fetches all active courses, ordered by end date and start date descending.
    """
    return Course.objects.filter(end_date__isnull=False, is_active=True).order_by(
        "-end_date", "-start_date"
    )
