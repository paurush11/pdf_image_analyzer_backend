from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.jobs"
    label = "jobs"

    def ready(self):
        try:
            from apps.jobs import models  # noqa: F401
            from apps.jobs.interfaces.django import admin  # noqa: F401
        except Exception:
            pass
