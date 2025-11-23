import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class FileStatus(models.TextChoices):
    UPLOADING = "uploading", "Uploading"
    AVAILABLE = "available", "Available"
    PROCESSING = "processing", "Processing"
    DONE = "done", "Done"
    ERROR = "error", "Error"


class UploadBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="upload_batches",
    )
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "upload_batch"
        indexes = [models.Index(fields=["user", "created_at"])]


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files"
    )
    # IMPORTANT: your session_id is hex, not a UUID object → store as CharField
    upload_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    batch = models.ForeignKey(
        UploadBatch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="files",
    )

    bucket = models.CharField(max_length=128)
    key = models.CharField(max_length=1024, db_index=True)

    content_type = models.CharField(max_length=255, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    storage_class = models.CharField(max_length=32, blank=True)
    etag = models.CharField(max_length=128, blank=True)
    checksum_sha256 = models.CharField(max_length=128, blank=True)

    status = models.CharField(
        max_length=16,
        choices=FileStatus.choices,
        default=FileStatus.AVAILABLE,
        db_index=True,
    )

    created_at = models.DateTimeField(default=timezone.now)
    available_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    error_code = models.CharField(max_length=64, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "file"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["bucket", "key"]),
        ]
