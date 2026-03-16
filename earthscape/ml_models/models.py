from django.conf import settings
from django.db import models

from data_processing.models import ProcessingJob


class ClimateModel(models.Model):
    class ModelType(models.TextChoices):
        ANOMALY_DETECTION = "anomaly_detection", "Anomaly Detection"
        TREND_PREDICTION = "trend_prediction", "Trend Prediction"
        CORRELATION = "correlation", "Correlation Analysis"

    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=40, choices=ModelType.choices)
    version = models.CharField(max_length=40)
    metrics = models.JSONField(default=dict, blank=True)
    artifact_path = models.CharField(max_length=400)
    trained_on = models.ForeignKey(
        ProcessingJob,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trained_models",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_ml_models",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "version")

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class Prediction(models.Model):
    climate_model = models.ForeignKey(ClimateModel, on_delete=models.CASCADE, related_name="predictions")
    target_date = models.DateField()
    region = models.CharField(max_length=120)
    signal = models.CharField(max_length=120)
    value = models.FloatField()
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-target_date", "region"]

    def __str__(self) -> str:
        return f"{self.region} {self.signal} {self.target_date}"
