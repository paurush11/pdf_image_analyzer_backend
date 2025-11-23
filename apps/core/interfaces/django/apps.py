from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"

    def ready(self):
        try:
            from apps.core import models  # noqa: F401
            from apps.core.interfaces.django import middleware  # noqa: F401
        except Exception:
            pass
