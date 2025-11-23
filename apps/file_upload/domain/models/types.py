from __future__ import annotations
from enum import Enum


class ProviderEnum(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class UploadStatus(str, Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    COMPLETING = "completing"
    AVAILABLE = "available"
    ERROR = "error"


class UploadType(str, Enum):
    SINGLE_PART = "single_part"
    MULTI_PART = "multi_part"
    RESUMABLE = "resumable"
