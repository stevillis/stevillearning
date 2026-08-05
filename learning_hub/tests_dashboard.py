"""Tests for the dashboard service."""

from django.test import TestCase
from django.utils import timezone

from learning_hub.models import (
    Category,
    Certification,
    Course,
    Formation,
    Institution,
)
from learning_hub.services import dashboard_service


class DashboardServiceTest(TestCase):
    """Tests for the dashboard service."""

    def setUp(self):
        """Set up test data for dashboard service tests."""
        # Create dummy data
        self.institution = Institution.objects.create(name="Test Inst")
        self.category = Category.objects.create(name="Test Cat")

        # Completed course
        self.course1 = Course.objects.create(
            name="Course 1",
            workload=10,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            institution=self.institution,
        )

        # In-progress course
        self.course2 = Course.objects.create(
            name="Course 2",
            workload=20,
            start_date=timezone.now().date(),
            institution=self.institution,
        )

        # Inactive course
        self.course3 = Course.objects.create(
            name="Course 3",
            workload=15,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            institution=self.institution,
            is_active=False,
        )

        # Formation
        self.formation = Formation.objects.create(
            name="Formation 1",
            workload=100,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
        )

        # Certification
        self.cert1 = Certification.objects.create(
            name="AWS Certified Solutions Architect",
            issue_date=timezone.now().date(),
            institution=self.institution,
        )

    def test_get_dashboard_stats(self):
        """Test retrieving dashboard statistics."""
        stats = dashboard_service.get_dashboard_stats()

        self.assertEqual(stats["total_courses"], 2)
        self.assertEqual(stats["total_formations"], 1)
        self.assertEqual(stats["total_certifications"], 1)
        self.assertEqual(stats["total_hours"], 30)
        self.assertEqual(stats["courses_completed"], 1)
        self.assertEqual(stats["courses_in_progress"], 1)

    def test_get_recent_activity(self):
        """Test retrieving recent activity."""
        activity = dashboard_service.get_recent_activity()
        self.assertTrue(len(activity) > 0)
        types = [item["type"] for item in activity]
        self.assertIn("Curso", types)
        self.assertIn("Certificação", types)
