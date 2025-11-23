from __future__ import annotations
from typing import Callable
from apps.file_upload.domain.models.dto import UploadCtx
from apps.file_upload.domain.models.types import ProviderEnum
from apps.file_upload.domain.ports.uploader import FileUploader
from apps.file_upload.domain.logic.partitioning import THRESHOLD
from apps.file_upload.infrastructure.aws.s3_single_uploader import (
    S3SingleFileUploader,
)
from apps.file_upload.infrastructure.aws.s3_multi_uploader import (
    S3MultiPartFileUploader,
)


class UploaderFactory:
    def __init__(
        self,
        s3_single: Callable[[], FileUploader] = lambda: S3SingleFileUploader(),
        s3_multi: Callable[[], FileUploader] = lambda: S3MultiPartFileUploader(),
        threshold_bytes: int = THRESHOLD,
    ):
        self._s3_single = s3_single
        self._s3_multi = s3_multi
        self._threshold = threshold_bytes

    def for_ctx(self, ctx: UploadCtx) -> FileUploader:
        if ctx.provider == ProviderEnum.AWS.value:
            if ctx.file_meta.size_bytes > self._threshold:
                return self._s3_multi()
            return self._s3_single()
        raise NotImplementedError(
            f"Uploader not implemented for provider={ctx.provider}"
        )
