from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    label = "analytics"

    def ready(self):
        try:
            from apps.analytics import models  # noqa: F401
            from apps.analytics.interfaces.django import admin  # noqa: F401
        except Exception:
            pass
