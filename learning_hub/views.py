from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from learning_hub.services import (
    certification_service,
    course_service,
    dashboard_service,
    formation_services,
)


def index(request):
    """Render the index page with dashboard statistics and recent activity."""
    stats = dashboard_service.get_dashboard_stats()
    recent_activity = dashboard_service.get_recent_activity()

    context = {**stats, "recent_activity": recent_activity}
    return render(request, "index.html", context)


def projects(request):
    """Render the projects page."""
    context = {}
    return render(request, "projects.html", context)


def formations(request):
    """Render the formations page with all formations."""
    formations_list = formation_services.get_all_formations()
    paginator = Paginator(formations_list, 5)
    page = request.GET.get("page")
    try:
        formations_qs = paginator.page(page)
    except PageNotAnInteger:
        formations_qs = paginator.page(1)
    except EmptyPage:
        formations_qs = paginator.page(paginator.num_pages)

    context = {
        "formations_qs": formations_qs,
    }
    return render(request, "formations.html", context)


def course(request, pk):
    """Render the course detail page."""
    course_found = course_service.get_course(pk=pk)
    context = {"course": course_found}
    return render(request, "course.html", context)


def courses(request):
    """Render the courses page with all courses."""
    courses_list = course_service.get_courses()
    paginator = Paginator(courses_list, 12)
    page = request.GET.get("page")
    try:
        courses_found = paginator.page(page)
    except PageNotAnInteger:
        courses_found = paginator.page(1)
    except EmptyPage:
        courses_found = paginator.page(paginator.num_pages)

    context = {"courses": courses_found}
    return render(request, "courses.html", context)


def certification(request, pk):
    """Render the certification detail page."""
    certification_found = certification_service.get_certification(pk=pk)
    context = {"certification": certification_found}
    return render(request, "certification.html", context)


def certifications(request):
    """Render the certifications page with all certifications."""
    certifications_list = certification_service.get_certifications()
    paginator = Paginator(certifications_list, 12)
    page = request.GET.get("page")
    try:
        certifications_found = paginator.page(page)
    except PageNotAnInteger:
        certifications_found = paginator.page(1)
    except EmptyPage:
        certifications_found = paginator.page(paginator.num_pages)

    context = {"certifications": certifications_found}
    return render(request, "certifications.html", context)
