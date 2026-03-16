from django.db import models

from data_ingestion.models import ClimateDataset


class ProcessingJob(models.Model):
    class JobType(models.TextChoices):
        MAP_REDUCE = "map_reduce", "MapReduce"
        STREAMING = "streaming", "Streaming"
        HYBRID = "hybrid", "Hybrid"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    dataset = models.ForeignKey(ClimateDataset, on_delete=models.CASCADE, related_name="processing_jobs")
    job_type = models.CharField(max_length=20, choices=JobType.choices)
    algorithm = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    config = models.JSONField(default=dict, blank=True)
    output_path = models.CharField(max_length=400, blank=True)
    result_summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.algorithm} ({self.job_type})"
