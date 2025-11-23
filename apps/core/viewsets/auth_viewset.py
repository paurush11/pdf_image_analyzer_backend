# apps/core/interfaces/django/viewsets_auth.py
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.core.services.auth_service import AuthService, SignupDTO
from apps.core.serializers.auth import (
    SignupSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    VerifyTokenSerializer,
)
import logging

logger = logging.getLogger(__name__)


def _fmt_exp(exp: int | None):
    if exp is None:
        return None
    return timezone.datetime.fromtimestamp(
        exp, tz=timezone.get_current_timezone()
    ).isoformat()


def _remaining(exp: int | None) -> int | None:
    if exp is None:
        return None
    now = int(timezone.now().timestamp())
    return max(exp - now, 0)


class AuthViewSet(viewsets.ViewSet):
    """
    AuthViewSet for the core app.
    """

    permission_classes = [permissions.AllowAny]
    auth_service = AuthService()

    # -------------------------
    # Email/password signup
    # -------------------------
    @swagger_auto_schema(
        method="post",
        request_body=SignupSerializer,
        responses={200: openapi.Response("OK")},
        operation_summary="Register (Cognito + local User)",
        tags=["Auth"],
    )
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        """
        Register a new user.
        """
        ser = SignupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        dto = SignupDTO(
            email=data["email"],
            username=data["username"],
            password=data["password"],
            given_name=data["givenName"],
            phone=data["phone"],
            name=data.get("name"),
        )
        try:
            self.auth_service.sign_up(dto)
        except Exception as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Successfully created. Please verify your email with the code sent."
            },
            status=status.HTTP_200_OK,
        )

    # -------------------------
    # Verify email
    # -------------------------
    @swagger_auto_schema(
        method="post",
        request_body=VerifyEmailSerializer,
        responses={200: openapi.Response("OK")},
        operation_summary="Confirm email with verification code",
        tags=["Auth"],
    )
    @action(detail=False, methods=["post"], url_path="verify")
    def verify(self, request):
        """
        Confirm email with verification code.
        """
        ser = VerifyEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        identifier = data.get("username") or data.get("email")
        if not identifier:
            return Response(
                {"message": "Email or username is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.auth_service.confirm_email(identifier=identifier, code=data["code"])
        except Exception as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Email verified successfully! You can now log in."},
            status=status.HTTP_200_OK,
        )

    # -------------------------
    # Login (username/email + password)
    # -------------------------
    @swagger_auto_schema(
        method="post",
        request_body=LoginSerializer,
        responses={200: openapi.Response("OK")},
        operation_summary="Login with username or email + password",
        tags=["Auth"],
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """
        Login with username or email + password.
        """
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        identifier = data.get("username") or data.get("email")
        if not identifier:
            return Response(
                {"message": "Username or email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = self.auth_service.login(
                identifier=identifier, password=data["password"]
            )
        except Exception as exc:
            return Response({"message": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        auth = result.get("AuthenticationResult") or {}
        return Response(
            {
                "message": "Login successful",
                "accessToken": auth.get("AccessToken"),
                "idToken": auth.get("IdToken"),
                "refreshToken": auth.get("RefreshToken"),
                "tokenType": auth.get("TokenType"),
                "expiresIn": auth.get("ExpiresIn"),
            },
            status=status.HTTP_200_OK,
        )

    # -------------------------
    # Refresh token
    # -------------------------
    @swagger_auto_schema(
        method="post",
        request_body=RefreshTokenSerializer,
        responses={200: openapi.Response("OK")},
        operation_summary="Refresh access token",
        tags=["Auth"],
    )
    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        """
        Refresh access token.
        """
        ser = RefreshTokenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        try:
            result = self.auth_service.refresh(
                refresh_token=data["refreshToken"], email=data["email"]
            )
        except Exception as exc:
            return Response({"message": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        auth = result.get("AuthenticationResult") or {}
        return Response(
            {
                "message": "Token refreshed successfully",
                "accessToken": auth.get("AccessToken"),
                "idToken": auth.get("IdToken"),
                "tokenType": auth.get("TokenType"),
                "expiresIn": auth.get("ExpiresIn"),
            },
            status=status.HTTP_200_OK,
        )

    # -------------------------
    # Verify token
    # -------------------------
    @swagger_auto_schema(
        method="post",
        request_body=VerifyTokenSerializer,
        responses={200: openapi.Response("OK")},
        operation_summary="Verify an access token",
        tags=["Auth"],
    )
    @action(detail=False, methods=["post"], url_path="verify-token")
    def verify_token(self, request):
        """
        Verify an access token.
        """
        ser = VerifyTokenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["token"]

        try:
            payload = self.auth_service.verify_access_token(token)
        except Exception as exc:
            return Response(
                {"message": str(exc), "valid": False},
                status=status.HTTP_403_FORBIDDEN,
            )

        exp = payload.get("exp")
        return Response(
            {
                "message": "Token is valid",
                "valid": True,
                "userId": payload.get("sub"),
                "userName": payload.get("username") or payload.get("cognito:username"),
                "expiresAt": exp,
                "expiresAtFormatted": _fmt_exp(exp),
                "isExpired": _remaining(exp) == 0 if exp else None,
                "remainingSeconds": _remaining(exp),
            },
            status=status.HTTP_200_OK,
        )

    # -------------------------
    # Health check
    # -------------------------
    @swagger_auto_schema(
        method="get",
        responses={200: openapi.Response("OK")},
        operation_summary="Health check",
        tags=["Auth"],
    )
    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request):
        """
        Health check.
        """
        return Response(
            {
                "status": "ok",
                "timestamp": timezone.now().isoformat(),
                "path": request.path,
            },
            status=status.HTTP_200_OK,
        )

    # -------------------------
    # Google OAuth: initiate login
    # -------------------------
    @swagger_auto_schema(
        method="get",
        responses={302: openapi.Response("Redirect to Cognito Google OAuth")},
        operation_summary="Initiate Google login via Cognito",
        tags=["Auth"],
    )
    @action(detail=False, methods=["get"], url_path="google")
    def google(self, request):
        """
        Redirect to Cognito's /oauth2/authorize endpoint for Google OAuth.
        """
        params = {
            "response_type": "code",
            "client_id": settings.AWS_COGNITO_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "identity_provider": "Google",
            "scope": "openid email",
        }
        auth_url = f"{settings.AWS_COGNITO_DOMAIN}/oauth2/authorize?{urlencode(params)}"
        return redirect(auth_url)

    # -------------------------
    # Google OAuth: callback
    # -------------------------
    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_QUERY,
                description="Authorization code returned by Cognito",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "error",
                openapi.IN_QUERY,
                description="OAuth error",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "error_description",
                openapi.IN_QUERY,
                description="OAuth error description",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: openapi.Response("OK")},
        operation_summary="Google OAuth callback",
        tags=["Auth"],
    )
    @action(detail=False, methods=["get"], url_path="google/callback")
    def google_callback(self, request):
        """
        Handle Google OAuth callback via Cognito (code → tokens → user info).
        NOTE: This is called by the frontend with ?code=..., not by Cognito directly.
        """
        code = request.query_params.get("code")
        error = request.query_params.get("error")
        error_description = request.query_params.get("error_description")

        if error:
            return Response(
                {
                    "message": "OAuth authentication failed",
                    "error": error,
                    "error_description": error_description,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code:
            return Response(
                {"message": "Authorization code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = self.auth_service.google_login(code)
        except Exception as exc:
            return Response(
                {
                    "message": "Failed to complete Google authentication",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Google login successful",
                "accessToken": result.get("accessToken"),
                "idToken": result.get("idToken"),
                "refreshToken": result.get("refreshToken"),
                "tokenType": result.get("tokenType"),
                "expiresIn": result.get("expiresIn"),
                "user": result.get("user"),
            },
            status=status.HTTP_200_OK,
        )
