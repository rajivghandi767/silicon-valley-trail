from typing import Any
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.conf import settings
import time
import os


@csrf_exempt
@require_http_methods(["GET"])
def health_detailed(request: HttpRequest) -> JsonResponse:
    """
    Comprehensive health check for production monitoring
    """
    checks: dict[str, dict[str, str]] = {}
    health_data: dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "svt-backend",
        "checks": checks,
    }

    overall_status = 200

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = 503

    # Static files check
    try:
        static_root = getattr(settings, "STATIC_ROOT", None)
        if static_root and os.path.exists(static_root):
            checks["static_files"] = {"status": "healthy"}
        else:
            checks["static_files"] = {
                "status": "warning",
                "message": "static files not found",
            }
    except Exception as e:
        checks["static_files"] = {"status": "unhealthy", "error": str(e)}

    # Set overall status
    if overall_status != 200:
        health_data["status"] = "unhealthy"

    return JsonResponse(health_data, status=overall_status)


@csrf_exempt
@require_http_methods(["GET"])
def health_simple(request: HttpRequest) -> JsonResponse:
    """
    Simple health check for load balancers and Docker healthchecks
    """
    return JsonResponse({"status": "ok"}, status=200)
