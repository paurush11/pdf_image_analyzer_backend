from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Model for user. User is saved in cognito and we store the user id here."""

    cognito_sub = models.UUIDField(unique=True, null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    test_user = models.BooleanField(default=False)
    google_user = models.BooleanField(default=False)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "core"

    def __str__(self):
        return self.username or (self.email or str(self.pk))
