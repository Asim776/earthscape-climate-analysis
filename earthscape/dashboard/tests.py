from django.test import TestCase
from django.urls import reverse

from users.models import User


class DashboardTests(TestCase):
    def test_dashboard_summary_endpoint(self):
        user = User.objects.create_user(username="admin", password="pass1234", role=User.Role.ADMINISTRATOR)
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard-summary"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("datasets", response.json())
