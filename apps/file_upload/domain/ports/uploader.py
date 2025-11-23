from __future__ import annotations
from typing import Protocol
from apps.file_upload.domain.models.dto import UploadCtx, UploadPlan, CompletionPayload


class FileUploader(Protocol):
    def plan(self, ctx: UploadCtx) -> UploadPlan: ...
    def complete(self, payload: CompletionPayload) -> None: ...
