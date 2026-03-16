import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from .models import User


def _load_json(request: HttpRequest):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_http_methods(["POST"])
def register(request: HttpRequest):
    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    username = payload.get("username")
    password = payload.get("password")
    role = payload.get("role", User.Role.VIEWER)
    if not username or not password:
        return JsonResponse({"error": "username and password are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "username already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=payload.get("email", ""),
        role=role,
        organization=payload.get("organization", ""),
    )
    return JsonResponse({"id": user.id, "username": user.username, "role": user.role}, status=201)


@require_http_methods(["POST"])
def login_view(request: HttpRequest):
    payload = _load_json(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid JSON payload")

    user = authenticate(request, username=payload.get("username"), password=payload.get("password"))
    if user is None:
        return JsonResponse({"error": "invalid credentials"}, status=401)

    login(request, user)
    return JsonResponse({"message": "logged in", "role": user.role})


@require_http_methods(["POST"])
@login_required
def logout_view(request: HttpRequest):
    logout(request)
    return JsonResponse({"message": "logged out"})


@require_GET
@login_required
def profile(request: HttpRequest):
    user = request.user
    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "organization": user.organization,
        }
    )
