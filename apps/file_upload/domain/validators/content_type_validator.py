from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from apps.file_upload.domain.models.dto import UploadCtx


@dataclass
class ContentTypeValidator:
    allowed_content_types: Sequence[str] = ()

    def handle(self, ctx: UploadCtx) -> None:
        ct = (ctx.file_meta.content_type or "").lower()
        if self.allowed_content_types and ct not in self.allowed_content_types:
            raise ValueError(f"Invalid content type: {ctx.file_meta.content_type}")
