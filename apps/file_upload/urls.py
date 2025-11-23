from django.urls import include, path

app_name = "file_upload"

urlpatterns = [
    path("", include("apps.file_upload.interfaces.django.urls")),
]
