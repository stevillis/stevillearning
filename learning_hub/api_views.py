from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Certification, Course
from .serializers import CertificationSerializer, CourseSerializer


class SyncDataAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        courses = (
            Course.objects.filter(is_active=True)
            .select_related("institution")
            .order_by("-end_date")
        )

        course_data = CourseSerializer(courses, many=True, context={"request": request}).data

        return Response({"courses": course_data})


class SyncCertificationsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        certifications = (
            Certification.objects.filter(is_active=True)
            .select_related("institution")
            .order_by("-issue_date")
        )

        certification_data = CertificationSerializer(
            certifications, many=True, context={"request": request}
        ).data

        return Response({"certifications": certification_data})
