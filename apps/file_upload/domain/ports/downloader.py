from __future__ import annotations
from typing import Protocol


class FileDownloader(Protocol):
    def presign_get(self, bucket: str, key: str, expires: int = 900) -> str: ...
