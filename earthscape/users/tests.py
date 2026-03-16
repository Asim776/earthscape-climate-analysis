from django.test import TestCase
from django.urls import reverse

from .models import User


class UserAuthTests(TestCase):
    def test_register_user(self):
        response = self.client.post(
            reverse("register"),
            data={"username": "ana", "password": "strongpass123", "role": "analyst"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
