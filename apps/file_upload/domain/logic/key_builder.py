from __future__ import annotations
from datetime import datetime
import re


def safe_name(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9._\-]", "-", name)


def compute_prefix(user_sub: str, project_id: str, now: datetime) -> str:
    # trailing slash on purpose
    return f"user/{user_sub}/project/{project_id}/year={now:%Y}/month={now:%m}/day={now:%d}/"


def key_for_single(prefix: str, upload_id: str, seq: int, filename: str) -> str:
    # multiple files in one “session”
    return f"{prefix}{upload_id}/{seq:04d}__{safe_name(filename)}"


def key_for_multipart(prefix: str, upload_id: str, filename: str) -> str:
    # one file over many parts — same key for all parts
    return f"{prefix}{upload_id}/{safe_name(filename)}"
