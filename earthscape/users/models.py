from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
        ('viewer', 'Viewer'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    # 🔥 AUTO SYNC ROLE WITH DJANGO PERMISSIONS
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        elif self.is_staff and self.role == 'viewer':
            self.role = 'analyst'
        super().save(*args, **kwargs)