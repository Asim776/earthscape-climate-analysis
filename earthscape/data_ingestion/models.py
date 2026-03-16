from django.conf import settings
from django.db import models


class DataSource(models.Model):
    class SourceType(models.TextChoices):
        SATELLITE = "satellite", "Satellite"
        WEATHER_STATION = "weather_station", "Weather Station"
        SENSOR = "sensor", "Environmental Sensor"
        FILE_UPLOAD = "file_upload", "File Upload"

    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=32, choices=SourceType.choices)
    format = models.CharField(max_length=32)
    endpoint = models.URLField(blank=True)
    is_realtime = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class ClimateDataset(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        INGESTED = "ingested", "Ingested"
        FAILED = "failed", "Failed"

    source = models.ForeignKey(DataSource, on_delete=models.PROTECT, related_name="datasets")
    name = models.CharField(max_length=255)
    hdfs_path = models.CharField(max_length=400)
    partition_key = models.CharField(max_length=120, blank=True)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
    row_count = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    missing_values = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_datasets",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} [{self.status}]"


class IngestionRun(models.Model):
    class RunStatus(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=20, choices=RunStatus.choices, default=RunStatus.QUEUED)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.PositiveBigIntegerField(default=0)
    error_message = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.source.name} - {self.status}"
