from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMINISTRATOR = "administrator", "Administrator"
        ANALYST = "analyst", "Analyst"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    organization = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
