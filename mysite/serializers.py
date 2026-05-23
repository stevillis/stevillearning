from django.urls import reverse
from rest_framework import serializers

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    institution = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = [
            "name",
            "workload",
            "description",
            "start_date",
            "end_date",
            "url",
            "institution",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(reverse("course", args=[obj.pk]))
        return reverse("course", args=[obj.pk])
