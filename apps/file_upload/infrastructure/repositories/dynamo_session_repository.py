from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional
from apps.file_upload.domain.models.dto import UploadCtx, UploadPlan
from apps.file_upload.domain.models.types import UploadStatus
from apps.file_upload.domain.ports.repository import SessionRepository
from apps.file_upload.domain.schemas.dynamo_session_schema import (
    FileUploadSessionSchema,
)
from apps.core.infrastructure.aws.clients import get_dynamodb_table


TABLE_NAME = "file_upload_session"


class DynamoSessionRepository(SessionRepository):
    def __init__(self, table_name: str = TABLE_NAME):
        self.table = get_dynamodb_table(table_name)

    # ---------- helpers ----------
    def _now_ts(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    def _get_by_gsi1(self, session_id: str) -> dict:
        resp = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression="#gpk = :gpk AND begins_with(#gsk, :gsk)",
            ExpressionAttributeNames={"#gpk": "GSI1PK", "#gsk": "GSI1SK"},
            ExpressionAttributeValues={":gpk": f"UPL#{session_id}", ":gsk": "SESS#"},
            Limit=1,
        )
        items = resp.get("Items", [])
        if not items:
            raise KeyError(f"session not found: {session_id}")
        return items[0]

    # ---------- required API ----------
    def create_session(self, ctx: UploadCtx, plan: UploadPlan) -> None:
        ttl = self._now_ts() + int(timedelta(days=7).total_seconds())
        item = FileUploadSessionSchema.new(
            user_sub=ctx.user_sub,
            upload_id=plan.upload_id,
            bucket=plan.bucket,
            key=plan.key,
            started_at=self._now_ts(),
            total_parts=plan.total_parts,
            bytes_total=ctx.file_meta.size_bytes,
            content_type=ctx.file_meta.content_type,
            ttl=ttl,
        ).to_dynamo()

        # conditional put to avoid duplicates
        self.table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
        )

    def set_status(self, session_id: str, status: str) -> None:
        item = self._get_by_gsi1(session_id)
        pk, sk = item["PK"], item["SK"]
        # Keep original ts in SK for ordering, recompute GSI2/3
        ts = sk.split("#")[1]
        self.table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET #st = :st, GSI2PK = :g2pk, GSI2SK = :g2sk, GSI3PK = :g3pk, GSI3SK = :g3sk",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={
                ":st": status,
                ":g2pk": f"STATUS#{status}",
                ":g2sk": f"{ts}#USER#{item['user_sub']}#{session_id}",
                ":g3pk": f"USER#{item['user_sub']}#STATUS#{status}",
                ":g3sk": f"{ts}#{session_id}",
            },
        )

    def mark_available(self, session_id: str, bucket: str, key: str) -> None:
        # no-op beyond status; but you could set completed_at, bytes_uploaded, etc.
        item = self._get_by_gsi1(session_id)
        self.table.update_item(
            Key={"PK": item["PK"], "SK": item["SK"]},
            UpdateExpression="SET completed_at = :t",
            ExpressionAttributeValues={":t": self._now_ts()},
        )

    def mark_error(self, session_id: str, code: str, message: str) -> None:
        item = self._get_by_gsi1(session_id)
        self.table.update_item(
            Key={"PK": item["PK"], "SK": item["SK"]},
            UpdateExpression="SET #st = :st, error_code = :c, error_message = :m",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={
                ":st": UploadStatus.ERROR.value,
                ":c": code,
                ":m": message,
            },
        )

    def save_multipart_id(self, session_id: str, mpu_upload_id: str) -> None:
        item = self._get_by_gsi1(session_id)
        self.table.update_item(
            Key={"PK": item["PK"], "SK": item["SK"]},
            UpdateExpression="SET s3_mpu_id = :u",
            ExpressionAttributeValues={":u": mpu_upload_id},
        )

    def get_ctx(self, session_id: str) -> UploadCtx:
        item = self._get_by_gsi1(session_id)
        # Rehydrate a minimal UploadCtx (provider can be stored in item if multi-cloud)
        from apps.file_upload.domain.models.dto import UploadCtx, FileMeta

        return UploadCtx(
            provider="aws",
            user_sub=item["user_sub"],
            project_id=item.get("project_id", "default"),
            prefix="/".join(item["key"].split("/")[:-1]) + "/",
            file_meta=FileMeta(
                filename=item["key"].split("/")[-1],
                content_type=item.get("content_type", "application/octet-stream"),
                size_bytes=int(item.get("bytes_total", 0)),
            ),
        )

    def get_plan(self, session_id: str) -> UploadPlan:
        item = self._get_by_gsi1(session_id)
        from apps.file_upload.domain.models.dto import UploadPlan
        from apps.file_upload.domain.models.types import UploadType

        return UploadPlan(
            upload_type=(
                UploadType.MULTI_PART
                if item.get("total_parts")
                else UploadType.SINGLE_PART
            ),
            upload_id=session_id,
            bucket=item["bucket"],
            key=item["key"],
            part_size=int(item.get("part_size") or 0) or None,
            total_parts=int(item.get("total_parts") or 0) or None,
        )

    def get_multipart_id(self, session_id: str) -> Optional[str]:
        item = self._get_by_gsi1(session_id)
        return item.get("s3_mpu_id")

    def abort_multipart(self, session_id: str) -> Optional[dict]:
        # If you want to actually call S3.abort_multipart_upload, you can do it here after storing bucket/key/mpu id
        return None
