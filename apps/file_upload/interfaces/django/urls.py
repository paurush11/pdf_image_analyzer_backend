from django.urls import path
from .viewsets.upload_viewset import UploadViewSet

v = UploadViewSet.as_view
urlpatterns = [
    path("upload/plan", v({"post": "plan"}), name="upload-plan"),
    path("upload/complete", v({"post": "complete"}), name="upload-complete"),
    path("download/presign", v({"post": "presign_download"}), name="download-presign"),
]
