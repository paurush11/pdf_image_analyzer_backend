# apps/file_upload/application/services/file_service.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from functools import lru_cache

from apps.file_upload.domain.models.dto import (
    UploadCtx,
    DownloadCtx,
    UploadPlan,
    CompletionPayload,
)
from apps.file_upload.domain.models.types import UploadStatus, UploadType
from apps.file_upload.domain.ports.uploader import FileUploader
from apps.file_upload.domain.ports.downloader import FileDownloader
from apps.file_upload.domain.ports.repository import SessionRepository

from apps.file_upload.application.factories.uploader_factory import UploaderFactory
from apps.file_upload.application.factories.downloader_factory import DownloaderFactory
from apps.file_upload.domain.validators.size_limit_validator import SizeLimitValidator
from apps.file_upload.domain.validators.content_type_validator import (
    ContentTypeValidator,
)
from apps.file_upload.domain.validators.empty_key_validator import EmptyKeyValidator

from apps.file_upload.infrastructure.repositories.dynamo_session_repository import (
    DynamoSessionRepository,
)


@dataclass
class FileService:
    uploader_factory: UploaderFactory
    downloader_factory: DownloaderFactory
    sessions: SessionRepository
    upload_validators: Sequence = (
        SizeLimitValidator(),
        ContentTypeValidator(allowed_content_types=()),
    )
    download_validators: Sequence = (EmptyKeyValidator(),)

    def plan_upload(self, ctx: UploadCtx) -> UploadPlan:
        for v in self.upload_validators:
            v.handle(ctx)
        uploader: FileUploader = self.uploader_factory.for_ctx(ctx)
        plan = uploader.plan(ctx)

        self.sessions.create_session(ctx, plan)
        if plan.upload_type == UploadType.MULTI_PART and plan.complete_url_payload:
            mpu = plan.complete_url_payload.get("mpu_upload_id")
            if mpu:
                self.sessions.save_multipart_id(plan.upload_id, mpu)

        self.sessions.set_status(plan.upload_id, UploadStatus.UPLOADING.value)
        return plan

    def complete_upload(self, payload: CompletionPayload) -> None:
        ctx = self.sessions.get_ctx(payload.session_id)
        plan = self.sessions.get_plan(payload.session_id)
        uploader = self.uploader_factory.for_ctx(ctx)
        try:
            uploader.complete(payload)
        except Exception as e:
            self.sessions.mark_error(plan.upload_id, "UPLOAD_ERROR", str(e))
            raise
        self.sessions.mark_available(plan.upload_id, plan.bucket, plan.key)
        self.sessions.set_status(plan.upload_id, UploadStatus.AVAILABLE.value)

    def abort_upload(self, session_id: str) -> None:
        try:
            self.sessions.abort_multipart(session_id)
        finally:
            self.sessions.mark_error(session_id, "UPLOAD_ABORTED", "Upload aborted")

    def presign_download(self, ctx: DownloadCtx) -> str:
        for v in self.download_validators:
            v.handle(ctx)
        dl: FileDownloader = self.downloader_factory.for_provider(ctx.provider)
        return dl.presign_get(ctx.bucket, ctx.key)


@lru_cache(maxsize=1)
def get_file_service() -> FileService:
    return FileService(
        uploader_factory=UploaderFactory(),
        downloader_factory=DownloaderFactory(),
        sessions=DynamoSessionRepository(),
    )


# (optional) test helper to reset the singleton between tests
def _reset_singleton_for_tests() -> None:
    get_file_service.cache_clear()  # pragma: no cover
