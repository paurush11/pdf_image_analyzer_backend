"""URL configuration for analytics app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.analytics.viewsets.analytics_viewset import AnalyticsViewSet

router = DefaultRouter()
router.register(r'', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]

