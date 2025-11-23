"""
Django settings for pdf_image_analyzer_backend project.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# ---------------------------
# Env helpers
# ---------------------------
def env(name, default=None):
    return os.getenv(name, default)


def env_int(name, default):
    return int(os.getenv(name, str(default)))


def env_bool(name, default=False):
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in {"1", "true", "yes", "y", "on"}


def env_csv(name, default=""):
    raw = os.getenv(name, default)
    return [s for s in (x.strip() for x in raw.split(",")) if s]


# ---------------------------
# Core
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_csv("ALLOWED_HOSTS") or [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "notebook-llm.paurushbatish.com/",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Optional: serve admin under a custom internal path
ADMIN_URL = env("ADMIN_URL", "admin/")

# ---------------------------
# Applications
# ---------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_filters",
    "django_extensions",
    "axes",
    "corsheaders",
    "bulk_update_or_create",
    "rest_framework",
    "drf_yasg",
    "pgvector.django",
    # Local apps
    "apps.core",
    "apps.file_upload",
    "apps.jobs",
    "apps.analytics",
]

# ---------------------------
# Auth / Axes / DRF
# ---------------------------
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",  # FIRST: protect admin login
    "django.contrib.auth.backends.ModelBackend",  # needed for /admin auth
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static for admin
    "corsheaders.middleware.CorsMiddleware",  # keep high
    "axes.middleware.AxesMiddleware",  # before session/auth
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # admin uses CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# DRF uses internal service JWT (Option B)
REST_FRAMEWORK = {
    # "DEFAULT_AUTHENTICATION_CLASSES": [
    #     "config.auth_internal.InternalServiceJWTAuthentication",
    # ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# ---------------------------
# Templates
# ---------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # you can add paths to custom templates here later
        "APP_DIRS": True,  # IMPORTANT: lets Django find templates inside apps (incl. drf_yasg)
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # needed by DRF & drf-yasg
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Axes config (Redis cache strongly recommended in prod)
AXES_ENABLED = True
AXES_FAILURE_LIMIT = env_int("AXES_FAILURE_LIMIT", 5)
AXES_COOLOFF_TIME = env_int("AXES_COOLOFF_TIME", 60)  # minutes
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_PROXY_COUNT = env_int("AXES_PROXY_COUNT", 1)
AXES_META_PRECEDENCE_ORDER = ["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"]
AXES_USE_USER_AGENT = True

# ---------------------------
# URLs / WSGI / ASGI
# ---------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
# (ASGI configured in Dockerfile via gunicorn+uvicorn worker)

# ---------------------------
# Database
# ---------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "notebook_llm"),
        "USER": env("DB_USER", "postgres"),
        "PASSWORD": env("DB_PASSWORD", "postgres"),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
    }
}

# ---------------------------
# Password validation
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------
# i18n / TZ
# ---------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------
# Static (WhiteNoise for admin static only)
# ---------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year

# ---------------------------
# CORS
# ---------------------------
CORS_ALLOWED_ORIGINS = env_csv("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# ---------------------------
# AWS knobs (if needed by code)
# ---------------------------
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", "")
AWS_REGION = env("AWS_REGION", "us-east-1")
AWS_COGNITO_USER_POOL_ID = env("AWS_COGNITO_USER_POOL_ID", "")
AWS_COGNITO_CLIENT_ID = env("AWS_COGNITO_CLIENT_ID", "")
AWS_COGNITO_CLIENT_SECRET = env("AWS_COGNITO_CLIENT_SECRET", "")
AWS_COGNITO_DOMAIN = env(
    "AWS_COGNITO_DOMAIN", ""
)  # https://your-domain.auth.us-east-1.amazoncognito.com

GOOGLE_REDIRECT_URI = env("GOOGLE_REDIRECT_URI", "")  # same as Node had
INTERNAL_SYNC_SECRET = env("INTERNAL_SYNC_SECRET", "change-me")

# ---------------------------
# Celery (runtime-only here; queues/routes/beat live in config/celery.py)
# ---------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = env("APP_TIMEZONE", "UTC")

CELERY_WORKER_PREFETCH_MULTIPLIER = env_int("CELERY_PREFETCH", 1)
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TIME_LIMIT = env_int("TASK_TIME_LIMIT", 30 * 60)
CELERY_TASK_SOFT_TIME_LIMIT = env_int("TASK_SOFT_TIME_LIMIT", 25 * 60)
CELERY_WORKER_ENABLE_REMOTE_CONTROL = True
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = env_int("BROKER_CONN_MAX_RETRIES", 100)
CELERY_BROKER_HEARTBEAT = env_int("BROKER_HEARTBEAT", 30)

# SQS transport tuning (applies when broker is sqs://)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": env("AWS_DEFAULT_REGION", "us-east-1"),
    "wait_time_seconds": env_int("SQS_WAIT_TIME_SECONDS", 20),
    "visibility_timeout": env_int("SQS_VISIBILITY_TIMEOUT", 15 * 60),
    "polling_interval": float(env("SQS_POLLING_INTERVAL", "0")),
}

CELERY_RESULT_EXPIRES = env_int("CELERY_RESULT_EXPIRES", 3600)

# Flower (optional; for local/dev)
FLOWER_PORT = env_int("FLOWER_PORT", 5555)
FLOWER_BROKER_API = CELERY_BROKER_URL

# ---------------------------
# Swagger / drf-yasg
# ---------------------------
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "delete", "patch"],
    "OPERATIONS_SORTER": "alpha",
    "TAGS_SORTER": "alpha",
    "DOC_EXPANSION": "none",
    "DEEP_LINKING": True,
    "SHOW_EXTENSIONS": True,
    "DEFAULT_MODEL_RENDERING": "example",
}

# ---------------------------
# Test DB override
# ---------------------------
if "test" in sys.argv or "pytest" in sys.modules:
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}

AUTH_USER_MODEL = "core.User"
APPEND_SLASH = False
# ---------------------------
# Logging
# ---------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "jsonlite": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "jsonlite"},
    },
    "root": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO")},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
