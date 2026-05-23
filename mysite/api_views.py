from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course
from .serializers import CourseSerializer


class SyncDataAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        courses = (
            Course.objects.filter(is_active=True)
            .select_related("institution")
            .order_by("-end_date")
        )

        course_data = CourseSerializer(
            courses, many=True, context={"request": request}
        ).data

        return Response({"courses": course_data})
