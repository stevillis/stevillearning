"""Service functions for dashboard statistics and recent activities."""

from typing import Any

from django.db.models import Sum

from mysite.models import Certification, Course, Formation


def get_dashboard_stats() -> dict[str, Any]:
    """
    Calculates and returns statistics for the dashboard.
    """
    total_courses = Course.objects.filter(is_active=True).count()
    total_formations = Formation.objects.count()
    total_certifications = Certification.objects.filter(is_active=True).count()

    # Calculate total hours (sum of workload from all courses)
    total_hours_data = Course.objects.filter(is_active=True).aggregate(total_hours=Sum("workload"))
    total_hours = total_hours_data["total_hours"] or 0

    # Course progress
    courses_completed = Course.objects.filter(end_date__isnull=False, is_active=True).count()
    courses_in_progress = Course.objects.filter(end_date__isnull=True, is_active=True).count()

    return {
        "total_courses": total_courses,
        "total_formations": total_formations,
        "total_certifications": total_certifications,
        "total_hours": total_hours,
        "courses_completed": courses_completed,
        "courses_in_progress": courses_in_progress,
    }


def get_recent_activity(limit: int = 5) -> list[dict[str, Any]]:
    """
    Fetches the most recently completed courses and issued certifications.
    Returns a list sorted by date.
    """
    activities = []

    recent_courses = Course.objects.filter(end_date__isnull=False, is_active=True).order_by(
        "-end_date"
    )[:limit]

    for course in recent_courses:
        activities.append(
            {
                "type": "Curso",
                "id": course.pk,
                "description": f"{course.name} ({course.institution.name if course.institution else 'N/A'})",
                "end_date": course.end_date.strftime("%d/%m/%Y"),
                "timestamp": course.end_date,
            }
        )

    recent_certifications = Certification.objects.filter(is_active=True).order_by("-issue_date")[
        :limit
    ]

    for certification in recent_certifications:
        activities.append(
            {
                "type": "Certificação",
                "id": certification.pk,
                "description": f"{certification.name} ({certification.institution.name if certification.institution else 'N/A'})",
                "end_date": certification.issue_date.strftime("%d/%m/%Y"),
                "timestamp": certification.issue_date,
            }
        )

    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]
