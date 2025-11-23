from __future__ import annotations
import uuid
from config import settings
from apps.file_upload.domain.models.dto import UploadCtx, UploadPlan, CompletionPayload
from apps.file_upload.domain.models.types import UploadType
from apps.file_upload.domain.logic.partitioning import plan_part_size
from apps.file_upload.domain.logic.key_builder import key_for_multipart
from apps.core.infrastructure.aws.clients import get_s3_client


class S3MultiPartFileUploader:
    def __init__(self, s3_client=None):
        self.s3 = s3_client or get_s3_client()

    def plan(self, ctx: UploadCtx) -> UploadPlan:
        session_id = uuid.uuid4().hex
        key = key_for_multipart(ctx.prefix, session_id, ctx.file_meta.filename)

        init = self.s3.create_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            ContentType=ctx.file_meta.content_type,
        )
        mpu_upload_id: str = init["UploadId"]

        part_size, total_parts = plan_part_size(ctx.file_meta.size_bytes)
        part_urls = [
            self.s3.generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": key,  # SAME KEY for all parts
                    "UploadId": mpu_upload_id,
                    "PartNumber": i,
                },
                ExpiresIn=3600,
            )
            for i in range(1, total_parts + 1)
        ]

        return UploadPlan(
            upload_type=UploadType.MULTI_PART,
            upload_id=session_id,  # your session id (not S3’s)
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=key,
            part_size=part_size,
            total_parts=total_parts,
            part_urls=part_urls,
            complete_url_payload={
                "bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "key": key,
                "session_id": session_id,
                "mpu_upload_id": mpu_upload_id,
                "parts": [],
            },
        )

    def complete(self, payload: CompletionPayload) -> None:
        if not payload.mpu_upload_id or not payload.parts:
            raise ValueError("multipart completion requires mpu_upload_id and parts")
        self.s3.complete_multipart_upload(
            Bucket=payload.bucket,
            Key=payload.key,
            UploadId=payload.mpu_upload_id,
            MultipartUpload={"Parts": list(payload.parts)},
        )
