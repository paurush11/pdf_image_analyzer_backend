# apps/core/interfaces/django/services/auth_service.py
from dataclasses import dataclass
from typing import Any, Dict, Optional
import uuid
import base64
from datetime import datetime
import requests
from django.conf import settings
from django.utils import timezone

from apps.core.models import User
from apps.core.infrastructure.aws import cognito as cognito_client
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignupDTO:
    email: str
    username: str
    password: str
    given_name: str
    phone: str
    name: Optional[str] = None


class AuthService:
    # -------------------------
    # Email/password flows
    # -------------------------
    def sign_up(self, data: SignupDTO) -> Dict[str, Any]:
        resp = cognito_client.sign_up(
            username=data.username,
            password=data.password,
            email=data.email,
            given_name=data.given_name,
            phone=data.phone,
            name=data.name,
        )
        sub = resp.get("UserSub")
        if sub:
            self._upsert_user(
                sub=sub,
                email=data.email,
                username=data.username,
                given_name=data.given_name,
            )
        return resp

    def confirm_email(self, identifier: str, code: str) -> Dict[str, Any]:
        return cognito_client.confirm_sign_up(username=identifier, code=code)

    def login(self, identifier: str, password: str) -> Dict[str, Any]:
        return cognito_client.login(identifier=identifier, password=password)

    def refresh(self, refresh_token: str, email: str) -> Dict[str, Any]:
        return cognito_client.refresh_token(refresh_token=refresh_token, email=email)

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        return cognito_client.verify_access_token(token)

    # -------------------------
    # Google OAuth via Cognito
    # -------------------------
    def _exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens using Cognito /oauth2/token.
        """
        token_url = f"{settings.AWS_COGNITO_DOMAIN}/oauth2/token"

        body = {
            "grant_type": "authorization_code",
            "client_id": settings.AWS_COGNITO_CLIENT_ID,
            "code": code,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }

        # Basic auth: client_id:client_secret
        raw_creds = (
            f"{settings.AWS_COGNITO_CLIENT_ID}:{settings.AWS_COGNITO_CLIENT_SECRET}"
        )
        b64_creds = base64.b64encode(raw_creds.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {b64_creds}",
        }

        resp = requests.post(token_url, data=body, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user info from Cognito's /oauth2/userInfo.
        """
        userinfo_url = f"{settings.AWS_COGNITO_DOMAIN}/oauth2/userInfo"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        resp = requests.get(userinfo_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def google_login(self, code: str) -> Dict[str, Any]:
        """
        Full Google -> Cognito flow:
        - exchange code for tokens
        - get user info
        - upsert local User
        - return tokens + user shape for frontend
        """
        token_data = self._exchange_code_for_tokens(code)
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("No access_token in token response")

        user_info = self._get_user_info(access_token)

        # Raw fields from Cognito userInfo
        sub = user_info.get("sub")
        email = user_info.get("email") or ""

        preferred_username = user_info.get("preferred_username")
        cognito_username = user_info.get("username")
        given_name = user_info.get("given_name") or user_info.get("name")
        name = (
            user_info.get("name")
            or given_name
            or (email.split("@")[0] if email else None)
        )

        username = preferred_username or cognito_username or email

        user = None
        if sub and email:
            user = self._upsert_user(
                sub=sub,
                email=email,
                username=username,
                given_name=given_name,
                google_user=True,
            )

        return {
            "accessToken": token_data.get("access_token"),
            "idToken": token_data.get("id_token"),
            "refreshToken": token_data.get("refresh_token"),
            "tokenType": token_data.get("token_type"),
            "expiresIn": token_data.get("expires_in"),
            "user": {
                "sub": sub,
                "email": email,
                "emailVerified": user_info.get("email_verified"),
                "givenName": given_name,
                "name": name,
                "username": username,
                "localUserId": str(user.pk) if user is not None else None,
            },
        }

    # -------------------------
    # Local user upsert
    # -------------------------
    def _upsert_user(
        self,
        *,
        sub: str,
        email: str,
        username: Optional[str],
        given_name: Optional[str],
        google_user: Optional[bool] = False,
    ) -> User:
        """
        Create or update a local User row corresponding to a Cognito user.
        """
        try:
            sub_uuid = uuid.UUID(sub)
        except ValueError:
            raise ValueError(f"Invalid Cognito sub, not a UUID: {sub!r}")

        # ✅ Make sure username is never null/empty
        safe_username = (username or email or "").strip()
        if not safe_username:
            raise ValueError("Cannot upsert user without a username or email")

        defaults = {
            "email": email,
            "username": safe_username,
            "updated_at": timezone.now(),
            "google_user": google_user,
            # use timezone-aware now
            **({"last_login": timezone.now()} if google_user else {}),
        }

        if hasattr(User, "first_name") and given_name:
            defaults["first_name"] = given_name
        if hasattr(User, "is_active"):
            defaults["is_active"] = True

        user, _ = User.objects.update_or_create(
            cognito_sub=sub_uuid,
            defaults=defaults,
        )
        return user
