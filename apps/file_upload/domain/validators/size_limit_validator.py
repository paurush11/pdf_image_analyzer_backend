from __future__ import annotations
from dataclasses import dataclass
from apps.file_upload.domain.models.dto import UploadCtx


@dataclass
class SizeLimitValidator:
    max_size_bytes: int = 5 * 1024 * 1024 * 1024  # 5GB default

    def handle(self, ctx: UploadCtx) -> None:
        if ctx.file_meta.size_bytes > self.max_size_bytes:
            raise ValueError(f"File size exceeds limit: {self.max_size_bytes}")
