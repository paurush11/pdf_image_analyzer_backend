from __future__ import annotations
from typing import Optional, Dict, Any, Literal
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    NonNegativeInt,
    PositiveInt,
)
from datetime import datetime, timezone
from apps.file_upload.domain.models.types import UploadStatus, UploadType


class FileUploadSessionSchema(BaseModel):
    """
    Session header:
      PK  = USER#<sub>
      SK  = SESS#<yyyyMMddHHmmss>#<upload_id>
      GSI1PK = UPL#<upload_id>, GSI1SK = SESS#<ts>#<upload_id>
      GSI2PK = STATUS#<status>, GSI2SK = <ts>#USER#<sub>#<upload_id>
      GSI3PK = USER#<sub>#STATUS#<status>, GSI3SK = <ts>#<upload_id>
    """

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    pk: str = Field(..., alias="PK")
    sk: str = Field(..., alias="SK")
    gsi1_pk: str = Field(..., alias="GSI1PK")
    gsi1_sk: str = Field(..., alias="GSI1SK")
    gsi2_pk: str = Field(..., alias="GSI2PK")
    gsi2_sk: str = Field(..., alias="GSI2SK")
    gsi3_pk: Optional[str] = Field(None, alias="GSI3PK")
    gsi3_sk: Optional[str] = Field(None, alias="GSI3SK")

    entity: Literal["session"] = "session"
    upload_type: UploadType = UploadType.MULTI_PART
    upload_id: str
    user_sub: str

    bucket: str
    key: str
    content_type: Optional[str] = None

    total_parts: Optional[PositiveInt] = None
    parts_received: NonNegativeInt = 0
    part_size: Optional[NonNegativeInt] = None

    bytes_total: Optional[NonNegativeInt] = None
    bytes_uploaded: NonNegativeInt = 0
    status: UploadStatus = UploadStatus.UPLOADING

    started_at: PositiveInt
    completed_at: Optional[PositiveInt] = None
    ttl: Optional[PositiveInt] = None

    @field_validator("pk")
    @classmethod
    def pk_must_start_with_user(cls, v: str) -> str:
        if not v.startswith("USER#"):
            raise ValueError('PK must start with "USER#"')
        return v

    @field_validator("sk")
    @classmethod
    def sk_must_be_session_header(cls, v: str) -> str:
        if not v.startswith("SESS#"):
            raise ValueError('SK must be "SESS#<ts>#<upload_id>"')
        return v

    @field_validator("parts_received")
    @classmethod
    def parts_received_le_total(cls, v: int, info) -> int:
        total = info.data.get("total_parts")
        if total is not None and v > total:
            raise ValueError("parts_received cannot exceed total_parts")
        return v

    def to_dynamo(self) -> Dict[str, Any]:
        data = self.model_dump(by_name=True)
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def new(
        cls,
        *,
        user_sub: str,
        upload_id: str,
        bucket: str,
        key: str,
        started_at: int,
        total_parts: Optional[int] = None,
        bytes_total: Optional[int] = None,
        content_type: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> "FileUploadSessionSchema":
        ts = datetime.fromtimestamp(started_at, tz=timezone.utc).strftime(
            "%Y%m%d%H%M%S"
        )
        sk = f"SESS#{ts}#{upload_id}"
        status = UploadStatus.UPLOADING.value
        return cls(
            PK=f"USER#{user_sub}",
            SK=sk,
            GSI1PK=f"UPL#{upload_id}",
            GSI1SK=sk,
            GSI2PK=f"STATUS#{status}",
            GSI2SK=f"{ts}#USER#{user_sub}#{upload_id}",
            GSI3PK=f"USER#{user_sub}#STATUS#{status}",
            GSI3SK=f"{ts}#{upload_id}",
            entity="session",
            upload_type=UploadType.MULTI_PART,
            upload_id=upload_id,
            user_sub=user_sub,
            bucket=bucket,
            key=key,
            content_type=content_type,
            total_parts=total_parts,
            parts_received=0,
            part_size=None,
            bytes_total=bytes_total,
            bytes_uploaded=0,
            status=UploadStatus.UPLOADING,
            started_at=started_at,
            completed_at=None,
            ttl=ttl,
        )
