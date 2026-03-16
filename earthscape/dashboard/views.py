import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from data_ingestion.models import ClimateDataset
from data_processing.models import ProcessingJob

from .models import AlertEvent, AlertRule, DashboardPreference, SupportTicket


def _load_json(request: HttpRequest):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_GET
@login_required
def dashboard_summary(request: HttpRequest):
    dataset_status = list(ClimateDataset.objects.values("status").annotate(total=Count("id")))
    job_status = list(ProcessingJob.objects.values("status").annotate(total=Count("id")))
    return JsonResponse(
        {
            "datasets": dataset_status,
            "processing_jobs": job_status,
            "active_alert_rules": AlertRule.objects.filter(is_active=True).count(),
            "open_support_tickets": SupportTicket.objects.filter(status=SupportTicket.TicketStatus.OPEN).count(),
        }
    )


@require_http_methods(["PUT"])
@login_required
def update_preferences(request: HttpRequest):
    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    preference, _ = DashboardPreference.objects.get_or_create(user=request.user)
    preference.layout = payload.get("layout", preference.layout)
    preference.filters = payload.get("filters", preference.filters)
    preference.save()
    return JsonResponse({"message": "preferences updated"})


@require_http_methods(["POST"])
@login_required
def create_alert_rule(request: HttpRequest):
    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    rule = AlertRule.objects.create(
        name=payload.get("name", "unnamed rule"),
        metric=payload.get("metric", "temperature"),
        operator=payload.get("operator", ">"),
        threshold=payload.get("threshold", 0),
        severity=payload.get("severity", AlertRule.Severity.MEDIUM),
        created_by=request.user,
    )
    return JsonResponse({"id": rule.id, "name": rule.name}, status=201)


@require_http_methods(["POST"])
@login_required
def raise_alert_event(request: HttpRequest, rule_id: int):
    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    rule = AlertRule.objects.filter(id=rule_id).first()
    if rule is None:
        return JsonResponse({"error": "rule not found"}, status=404)

    event = AlertEvent.objects.create(
        rule=rule,
        observed_value=payload.get("observed_value", 0),
        message=payload.get("message", "threshold reached"),
        delivered_to=payload.get("delivered_to", []),
    )
    return JsonResponse({"id": event.id, "delivery_status": event.delivery_status}, status=201)


@require_http_methods(["POST"])
@login_required
def create_support_ticket(request: HttpRequest):
    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    ticket = SupportTicket.objects.create(
        user=request.user,
        subject=payload.get("subject", "Support request"),
        description=payload.get("description", ""),
    )
    return JsonResponse({"id": ticket.id, "status": ticket.status}, status=201)
