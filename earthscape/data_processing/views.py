import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from data_ingestion.models import ClimateDataset
from users.models import User

from .models import ProcessingJob


def _load_json(request: HttpRequest):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_http_methods(["POST"])
@login_required
def create_processing_job(request: HttpRequest):
    if request.user.role not in {User.Role.ADMINISTRATOR, User.Role.ANALYST}:
        return JsonResponse({"error": "insufficient permissions"}, status=403)

    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    dataset = ClimateDataset.objects.filter(id=payload.get("dataset_id")).first()
    if dataset is None:
        return JsonResponse({"error": "dataset not found"}, status=404)

    job = ProcessingJob.objects.create(
        dataset=dataset,
        job_type=payload.get("job_type", ProcessingJob.JobType.MAP_REDUCE),
        algorithm=payload.get("algorithm", "anomaly_detector"),
        config=payload.get("config", {}),
    )
    return JsonResponse({"id": job.id, "status": job.status, "job_type": job.job_type}, status=201)


@require_GET
@login_required
def list_processing_jobs(request: HttpRequest):
    jobs = ProcessingJob.objects.select_related("dataset").values(
        "id", "job_type", "algorithm", "status", "dataset__name", "created_at"
    )
    return JsonResponse({"results": list(jobs)})
