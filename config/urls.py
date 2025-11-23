"""
URL configuration for pdf_image_analyzer_backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

SWAGGER_BASE_URL = "http://localhost:8000"
schema_view = get_schema_view(
    openapi.Info(
        title="PDF Image Analyzer API",
        default_version="v1",
        description=(
            "API for PDF and image analysis. "
            "This OpenAPI spec can be used with Orval for frontend code generation."
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=f"{SWAGGER_BASE_URL}/api/v1",
)


def health(_request):
    """Lightweight health check for ALB/ECS/Compose."""
    return JsonResponse({"ok": True, "service": "pdf_image_analyzer_backend"})


urlpatterns = [
    # Admin (customizable via settings.ADMIN_URL)
    path(getattr(settings, "ADMIN_URL", "admin/"), admin.site.urls),
    # Health check (compose & ALB reference this)
    path("health", health, name="health"),
    # API v1
    path("api/v1/file-upload/", include("apps.file_upload.urls")),
    path("api/v1/jobs/", include("apps.jobs.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/core/", include("apps.core.urls")),
    # OpenAPI schema for Orval (JSON/YAML) — always available internally
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]


if settings.DEBUG or getattr(settings, "ENABLE_API_DOCS", False):
    urlpatterns += [
        path(
            "api/v1/docs/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "api/v1/redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]
