import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from users.models import User

from .models import ClimateDataset, DataSource, IngestionRun


def _load_json(request: HttpRequest):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _can_manage_ingestion(user: User) -> bool:
    return user.role in {User.Role.ADMINISTRATOR, User.Role.ANALYST}


@require_GET
@login_required
def list_data_sources(request: HttpRequest):
    sources = DataSource.objects.filter(is_active=True).values(
        "id", "name", "source_type", "format", "is_realtime", "endpoint"
    )
    return JsonResponse({"results": list(sources)})


@require_http_methods(["POST"])
@login_required
def create_dataset(request: HttpRequest):
    if not _can_manage_ingestion(request.user):
        return JsonResponse({"error": "insufficient permissions"}, status=403)

    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    source_id = payload.get("source_id")
    source = DataSource.objects.filter(id=source_id).first()
    if source is None:
        return JsonResponse({"error": "invalid source_id"}, status=400)

    dataset = ClimateDataset.objects.create(
        source=source,
        name=payload.get("name", source.name),
        hdfs_path=payload.get("hdfs_path", ""),
        partition_key=payload.get("partition_key", ""),
        status=payload.get("status", ClimateDataset.Status.PENDING),
        uploaded_by=request.user,
        missing_values=payload.get("missing_values", 0),
        quality_score=payload.get("quality_score"),
    )
    return JsonResponse(
        {
            "id": dataset.id,
            "name": dataset.name,
            "hdfs_path": dataset.hdfs_path,
            "status": dataset.status,
        },
        status=201,
    )


@require_http_methods(["POST"])
@login_required
def trigger_ingestion_run(request: HttpRequest, source_id: int):
    if not _can_manage_ingestion(request.user):
        return JsonResponse({"error": "insufficient permissions"}, status=403)

    source = DataSource.objects.filter(id=source_id).first()
    if source is None:
        return JsonResponse({"error": "source not found"}, status=404)

    run = IngestionRun.objects.create(source=source, status=IngestionRun.RunStatus.QUEUED)
    return JsonResponse({"run_id": run.id, "source": source.name, "status": run.status}, status=202)


@require_GET
@login_required
def list_datasets(request: HttpRequest):
    datasets = ClimateDataset.objects.select_related("source").values(
        "id", "name", "status", "hdfs_path", "source__name", "created_at"
    )
    return JsonResponse({"results": list(datasets)})
