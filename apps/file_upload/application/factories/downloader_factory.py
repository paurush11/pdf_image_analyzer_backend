from __future__ import annotations
from apps.file_upload.domain.ports.downloader import FileDownloader
from apps.file_upload.infrastructure.aws.s3_downloader import S3Downloader
from apps.file_upload.domain.models.types import ProviderEnum


class DownloaderFactory:
    def for_provider(self, provider: str) -> FileDownloader:
        if provider == ProviderEnum.AWS.value:
            return S3Downloader()
        raise NotImplementedError(f"Downloader not implemented for provider={provider}")
