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


class FileUploadPartSchema(BaseModel):
    """
    Part item:
      PK = USER#<sub>
      SK = PART#<upload_id>#<part_number_padded>
      GSI1PK = UPL#<upload_id>
      GSI1SK = PART#<part_number_padded>
    """

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    pk: str = Field(..., alias="PK")
    sk: str = Field(..., alias="SK")
    gsi1_pk: Optional[str] = Field(None, alias="GSI1PK")
    gsi1_sk: Optional[str] = Field(None, alias="GSI1SK")

    entity: Literal["part"] = "part"
    part_number: PositiveInt
    etag: str
    size: NonNegativeInt
    uploaded_at: PositiveInt  # epoch seconds

    @field_validator("pk")
    @classmethod
    def pk_must_start_with_user(cls, v: str) -> str:
        if not v.startswith("USER#"):
            raise ValueError('PK must start with "USER#"')
        return v

    @field_validator("sk")
    @classmethod
    def sk_must_be_part_key(cls, v: str) -> str:
        if not v.startswith("PART#"):
            raise ValueError('SK must be "PART#<upload_id>#<n>"')
        return v

    def to_dynamo(self) -> Dict[str, Any]:
        return self.model_dump(by_name=True)

    @classmethod
    def new(
        cls,
        *,
        user_sub: str,
        upload_id: str,
        part_number: int,
        etag: str,
        size: int,
        uploaded_at: int,
    ) -> "FileUploadPartSchema":
        pn_pad = f"{part_number:05d}"
        return cls(
            PK=f"USER#{user_sub}",
            SK=f"PART#{upload_id}#{pn_pad}",
            GSI1PK=f"UPL#{upload_id}",
            GSI1SK=f"PART#{pn_pad}",
            entity="part",
            part_number=part_number,  # int (not padded)
            etag=etag,
            size=size,
            uploaded_at=uploaded_at,
        )
