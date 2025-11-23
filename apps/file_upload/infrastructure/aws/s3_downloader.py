from __future__ import annotations
from typing import Optional, Dict, Any
from config import settings
from apps.file_upload.domain.ports.downloader import FileDownloader
from apps.core.infrastructure.aws.clients import get_s3_client


class S3Downloader(FileDownloader):
    """
    Minimal presigner for GET. You can add optional response overrides:
      - ResponseContentType
      - ResponseContentDisposition (e.g., 'attachment; filename="name.pdf"')
    """

    def __init__(self, s3_client=None):
        self.s3 = s3_client or get_s3_client()

    def presign_get(
        self,
        bucket: str,
        key: str,
        expires: int = 900,
        *,
        response_headers: Optional[Dict[str, Any]] = None,
    ) -> str:
        params: Dict[str, Any] = {
            "Bucket": bucket or settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key,
        }
        if response_headers:
            params.update(response_headers)

        # raises if the client is misconfigured; fine to bubble up to service
        return self.s3.generate_presigned_url(
            ClientMethod="get_object",
            Params=params,
            ExpiresIn=expires,
        )
