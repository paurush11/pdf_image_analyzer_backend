from django.urls import include, path

app_name = "analytics"

urlpatterns = [
    path("", include("apps.analytics.interfaces.django.urls")),
]
from apps.analytics.interfaces.django.urls import urlpatterns

app_name = "analytics"
