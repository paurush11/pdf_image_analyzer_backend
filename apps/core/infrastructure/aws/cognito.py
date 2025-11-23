# apps/core/infrastructure/aws/cognito_client.py
import base64
import hashlib
import hmac
from typing import Any, Dict, Optional

import boto3
import requests
from django.conf import settings
from jose import jwt, JWTError


def _client():
    return boto3.client("cognito-idp", region_name=settings.AWS_REGION)


def _secret_hash(username: str) -> Optional[str]:
    secret = getattr(settings, "AWS_COGNITO_CLIENT_SECRET", "")
    if not secret:
        return None
    msg = f"{username}{settings.AWS_COGNITO_CLIENT_ID}".encode()
    key = secret.encode()
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def sign_up(
    *,
    username: str,
    password: str,
    email: str,
    given_name: str,
    phone: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Very thin wrapper around Cognito SignUp.
    All validation is done by DRF (serializer) or Cognito itself.
    """
    client = _client()

    attrs = [
        {"Name": "email", "Value": email},
        {"Name": "given_name", "Value": given_name},
        {"Name": "phone_number", "Value": phone},
    ]
    if name:
        attrs.append({"Name": "name", "Value": name})

    params: Dict[str, Any] = {
        "ClientId": settings.AWS_COGNITO_CLIENT_ID,
        "Username": username,
        "Password": password,
        "UserAttributes": attrs,
    }

    s_hash = _secret_hash(username)
    if s_hash:
        params["SecretHash"] = s_hash

    return client.sign_up(**params)


def confirm_sign_up(*, username: str, code: str) -> Dict[str, Any]:
    client = _client()
    params: Dict[str, Any] = {
        "ClientId": settings.AWS_COGNITO_CLIENT_ID,
        "Username": username,
        "ConfirmationCode": code,
    }
    s_hash = _secret_hash(username)
    if s_hash:
        params["SecretHash"] = s_hash

    return client.confirm_sign_up(**params)


def login(*, identifier: str, password: str) -> Dict[str, Any]:
    client = _client()
    params: Dict[str, Any] = {
        "ClientId": settings.AWS_COGNITO_CLIENT_ID,
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": identifier,
            "PASSWORD": password,
        },
    }
    s_hash = _secret_hash(identifier)
    if s_hash:
        params["AuthParameters"]["SECRET_HASH"] = s_hash

    return client.initiate_auth(**params)


def refresh_token(*, refresh_token: str, email: str) -> Dict[str, Any]:
    client = _client()
    params: Dict[str, Any] = {
        "ClientId": settings.AWS_COGNITO_CLIENT_ID,
        "AuthFlow": "REFRESH_TOKEN_AUTH",
        "AuthParameters": {
            "REFRESH_TOKEN": refresh_token,
            "USERNAME": email,
        },
    }
    s_hash = _secret_hash(email)
    if s_hash:
        params["AuthParameters"]["SECRET_HASH"] = s_hash

    return client.initiate_auth(**params)


# ---- token verify ----

_JWKS_CACHE: Optional[Dict[str, Any]] = None


def _jwks() -> Dict[str, Any]:
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        url = (
            f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
            f"{settings.AWS_COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        _JWKS_CACHE = resp.json()
    return _JWKS_CACHE


def verify_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token,
            _jwks(),
            algorithms=["RS256"],
            audience=settings.AWS_COGNITO_CLIENT_ID,
            options={"verify_at_hash": False},
        )
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc
