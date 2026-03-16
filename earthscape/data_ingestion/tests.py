from django.test import TestCase
from django.urls import reverse

from users.models import User

from .models import ClimateDataset, DataSource


class DataIngestionTests(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(username="viewer", password="pass1234", role=User.Role.VIEWER)
        self.analyst = User.objects.create_user(username="analyst", password="pass1234", role=User.Role.ANALYST)
        self.source = DataSource.objects.create(
            name="NOAA Stream",
            source_type=DataSource.SourceType.WEATHER_STATION,
            format="csv",
            endpoint="https://example.com",
            is_realtime=True,
        )

    def test_viewer_cannot_create_dataset(self):
        self.client.force_login(self.viewer)
        response = self.client.post(
            reverse("create-dataset"),
            data={"source_id": self.source.id, "name": "daily", "hdfs_path": "/datasets/daily"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_analyst_can_create_dataset(self):
        self.client.force_login(self.analyst)
        response = self.client.post(
            reverse("create-dataset"),
            data={"source_id": self.source.id, "name": "daily", "hdfs_path": "/datasets/daily"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ClimateDataset.objects.count(), 1)
