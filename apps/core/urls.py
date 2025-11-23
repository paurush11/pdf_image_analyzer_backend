from django.urls import path, include
from apps.core.viewsets.auth_viewset import AuthViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)
router.register(r"auth", AuthViewSet, basename="auth")


urlpatterns = [
    path("", include(router.urls)),
]
