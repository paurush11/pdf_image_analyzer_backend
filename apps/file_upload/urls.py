"""URL configuration for file_upload app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.file_upload.viewsets.file_upload_viewset import FileUploadViewSet

router = DefaultRouter()
router.register(r'', FileUploadViewSet, basename='file-upload')

urlpatterns = [
    path('', include(router.urls)),
]

