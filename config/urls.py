"""
URL configuration for pdf_image_analyzer_backend project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="PDF Image Analyzer API",
      default_version='v1',
      description="API for PDF and image analysis. This OpenAPI specification can be used with Orval for frontend code generation.",
      terms_of_service="",
      contact=openapi.Contact(email=""),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

def health_check(request):
    """Health check endpoint."""
    return JsonResponse({'status': 'healthy', 'service': 'pdf_image_analyzer_backend'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/v1/file-upload/', include('apps.file_upload.urls')),
    path('api/v1/jobs/', include('apps.jobs.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
]

