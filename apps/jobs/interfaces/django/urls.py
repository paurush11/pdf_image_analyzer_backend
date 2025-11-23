"""URL configuration for jobs app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.jobs.interfaces.django.viewsets.job_viewset import JobViewSet

router = DefaultRouter()
router.register(r"", JobViewSet, basename="jobs")

urlpatterns = [
    path("", include(router.urls)),
]
