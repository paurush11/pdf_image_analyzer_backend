from __future__ import annotations
from apps.file_upload.domain.models.dto import DownloadCtx


class EmptyKeyValidator:
    def handle(self, ctx: DownloadCtx) -> None:
        if not ctx.key:
            raise ValueError("Key is required")
