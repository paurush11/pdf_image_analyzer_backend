"""URL configuration for jobs app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.jobs.viewsets.job_viewset import JobViewSet

router = DefaultRouter()
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]

