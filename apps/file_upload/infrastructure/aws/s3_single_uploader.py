from __future__ import annotations
import uuid
from config import settings
from apps.file_upload.domain.models.dto import UploadCtx, UploadPlan, CompletionPayload
from apps.file_upload.domain.models.types import UploadType
from apps.file_upload.domain.logic.key_builder import key_for_single
from apps.core.infrastructure.aws.clients import get_s3_client


class S3SingleFileUploader:
    def __init__(self, s3_client=None):
        self.s3 = s3_client or get_s3_client()

    def plan(self, ctx: UploadCtx) -> UploadPlan:
        session_id = uuid.uuid4().hex
        key = key_for_single(ctx.prefix, session_id, 1, ctx.file_meta.filename)
        url: str = self.s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": key,
                "ContentType": ctx.file_meta.content_type,
            },
            ExpiresIn=3600,
        )
        return UploadPlan(
            upload_type=UploadType.SINGLE_PART,
            upload_id=session_id,
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=key,
            put_url=url,
            complete_url_payload={
                "bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "key": key,
                "session_id": session_id,
            },
        )

    def complete(self, payload: CompletionPayload) -> None:
        # optional verification (e.g., head_object)
        return
