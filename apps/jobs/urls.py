from django.urls import include, path

app_name = "jobs"

urlpatterns = [
    path("", include("apps.jobs.interfaces.django.urls")),
]
from apps.jobs.interfaces.django.urls import urlpatterns

app_name = "jobs"
