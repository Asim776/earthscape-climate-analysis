import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from data_processing.models import ProcessingJob
from users.models import User

from .models import ClimateModel, Prediction


def _load_json(request: HttpRequest):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_http_methods(["POST"])
@login_required
def register_model(request: HttpRequest):
    if request.user.role not in {User.Role.ADMINISTRATOR, User.Role.ANALYST}:
        return JsonResponse({"error": "insufficient permissions"}, status=403)

    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    training_job = ProcessingJob.objects.filter(id=payload.get("trained_on_job_id")).first()
    model = ClimateModel.objects.create(
        name=payload.get("name", "climate-model"),
        model_type=payload.get("model_type", ClimateModel.ModelType.TREND_PREDICTION),
        version=payload.get("version", "1.0.0"),
        artifact_path=payload.get("artifact_path", "hdfs://models/default"),
        metrics=payload.get("metrics", {}),
        trained_on=training_job,
        updated_by=request.user,
    )
    return JsonResponse({"id": model.id, "name": model.name, "version": model.version}, status=201)


@require_http_methods(["POST"])
@login_required
def create_prediction(request: HttpRequest):
    if request.user.role not in {User.Role.ADMINISTRATOR, User.Role.ANALYST}:
        return JsonResponse({"error": "insufficient permissions"}, status=403)

    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    model = ClimateModel.objects.filter(id=payload.get("model_id")).first()
    if model is None:
        return JsonResponse({"error": "model not found"}, status=404)

    prediction = Prediction.objects.create(
        climate_model=model,
        target_date=payload.get("target_date"),
        region=payload.get("region", "global"),
        signal=payload.get("signal", "temperature_anomaly"),
        value=payload.get("value", 0.0),
        confidence=payload.get("confidence", 0),
        payload=payload.get("payload", {}),
    )
    return JsonResponse({"id": prediction.id, "region": prediction.region, "signal": prediction.signal}, status=201)


@require_GET
@login_required
def list_models(request: HttpRequest):
    models = ClimateModel.objects.values("id", "name", "model_type", "version", "updated_at")
    return JsonResponse({"results": list(models)})
