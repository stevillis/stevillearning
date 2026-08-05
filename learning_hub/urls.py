from django.urls import path

from .api_views import SyncCertificationsAPIView, SyncDataAPIView
from .views import certification, certifications, course, courses, formations, index

urlpatterns = [
    path("", index, name="index"),
    # path("projects/", projects, name="projects"),
    path("formations/", formations, name="formations"),
    path("course/<int:pk>", course, name="course"),
    path("courses/", courses, name="courses"),
    path("certification/<int:pk>", certification, name="certification"),
    path("certifications/", certifications, name="certifications"),
    path("api/courses/", SyncDataAPIView.as_view(), name="api_courses"),
    path(
        "api/certifications/",
        SyncCertificationsAPIView.as_view(),
        name="api_certifications",
    ),
]
