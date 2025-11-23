"""
Custom authentication backend for internal service-to-service requests.

This module provides a lightweight token-based authentication class that is
referenced from DRF's ``DEFAULT_AUTHENTICATION_CLASSES`` in ``config.settings``.
"""

import os
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "y", "on"}


class InternalServiceJWTAuthentication(BaseAuthentication):
    """
    Simple bearer token authentication for trusted internal services.

    Expected header::

        Authorization: Bearer <INTERNAL_SERVICE_TOKEN>

    The token value is compared against the ``INTERNAL_SERVICE_TOKEN`` environment
    variable. When ``INTERNAL_AUTH_DISABLE_IN_DEBUG`` is truthy *and* Django is
    running in ``DEBUG`` mode, authentication is bypassed to ease local
    development.
    """

    keyword = "Bearer"
    _service_user: Optional[AbstractBaseUser] = None

    def authenticate(self, request) -> Tuple[AbstractBaseUser, None]:
        if self._should_bypass_auth():
            return self._get_or_create_service_user(), None

        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header:
            raise AuthenticationFailed("Authorization header missing.")

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed("Invalid Authorization header.")

        provided_token = parts[1]
        expected_token = os.getenv("INTERNAL_SERVICE_TOKEN")

        if not expected_token:
            raise AuthenticationFailed("Internal token is not configured.")

        if provided_token != expected_token:
            raise AuthenticationFailed("Invalid internal service token.")

        return self._get_or_create_service_user(), None

    def authenticate_header(self, request) -> str:
        return f'{self.keyword} realm="internal"'

    def _should_bypass_auth(self) -> bool:
        return getattr(settings, "DEBUG", False) and _env_bool(
            "INTERNAL_AUTH_DISABLE_IN_DEBUG", False
        )

    def _get_or_create_service_user(self) -> AbstractBaseUser:
        if self.__class__._service_user is None:
            UserModel = get_user_model()
            username = os.getenv("INTERNAL_SERVICE_USERNAME", "internal_service")
            user, created = UserModel.objects.get_or_create(
                username=username,
                defaults={
                    "email": os.getenv(
                        "INTERNAL_SERVICE_EMAIL", "internal-service@example.com"
                    ),
                    "is_active": True,
                    "first_name": "Internal",
                    "last_name": "Service",
                },
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
            self.__class__._service_user = user
        return self.__class__._service_user
