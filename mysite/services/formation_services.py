from django.db.models import QuerySet

from mysite.models import Formation


def get_all_formations() -> QuerySet:
    return Formation.objects.all().order_by("-end_date", "-start_date")
