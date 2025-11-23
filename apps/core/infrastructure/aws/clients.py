# apps/core/aws/clients.py
from functools import lru_cache
from typing import Optional
from boto3 import client, resource
from botocore.config import Config
from config import settings

_base_cfg = Config(
    region_name=settings.AWS_REGION,
    retries={"max_attempts": 10, "mode": "adaptive"},
    read_timeout=10,
    connect_timeout=10,
    max_pool_connections=50,  # bump for concurrency
)

# S3 has a couple of extras we often want
_s3_cfg = _base_cfg.merge(
    Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"},  # or "path" if you need it
        user_agent_extra="file-upload-service/1.0",
    )
)


@lru_cache(maxsize=32)
def get_s3_client(endpoint_url: Optional[str] = None):
    return client("s3", config=_s3_cfg, endpoint_url=endpoint_url)


@lru_cache(maxsize=32)
def get_dynamodb_resource(endpoint_url: Optional[str] = None):
    return resource("dynamodb", config=_base_cfg, endpoint_url=endpoint_url)


@lru_cache(maxsize=128)
def get_dynamodb_table(table_name: str, endpoint_url: Optional[str] = None):
    # caching per table name + endpoint
    return get_dynamodb_resource(endpoint_url=endpoint_url).Table(table_name)


@lru_cache(maxsize=32)
def get_sqs_client(endpoint_url: Optional[str] = None):
    return client("sqs", config=_base_cfg, endpoint_url=endpoint_url)


@lru_cache(maxsize=32)
def get_sns_client(endpoint_url: Optional[str] = None):
    return client("sns", config=_base_cfg, endpoint_url=endpoint_url)
