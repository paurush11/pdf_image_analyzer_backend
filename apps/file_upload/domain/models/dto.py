from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence
from .types import ProviderEnum, UploadType


@dataclass(frozen=True)
class FileMeta:
    filename: str
    content_type: str
    size_bytes: int


@dataclass(frozen=True)
class UploadCtx:
    provider: ProviderEnum
    user_sub: str
    project_id: str
    file_meta: FileMeta
    prefix: str  # server-generated key prefix (e.g., user/project/yyyymm/)


@dataclass(frozen=True)
class DownloadCtx:
    provider: ProviderEnum
    bucket: str
    key: str


@dataclass(frozen=True)
class UploadPlan:
    upload_type: UploadType
    upload_id: str  # your session id (NOT S3 UploadId)
    bucket: str
    key: str
    part_size: Optional[int] = None
    total_parts: Optional[int] = None
    put_url: Optional[str] = None
    part_urls: Optional[Sequence[str]] = None
    complete_url_payload: Optional[dict] = None


@dataclass(frozen=True)
class CompletionPayload:
    provider: ProviderEnum
    bucket: str
    key: str
    session_id: str
    mpu_upload_id: Optional[str] = None
    parts: Optional[Sequence[dict]] = None  # [{"PartNumber": n, "ETag": "..."}]
    checksum: Optional[str] = None
