# apps/file_upload/interfaces/django/serializers.py
from __future__ import annotations
from rest_framework import serializers
from apps.file_upload.domain.models.types import ProviderEnum, UploadType
from apps.file_upload.interfaces.django.fields import EnumField


class FileMetaSerializer(serializers.Serializer):
    filename = serializers.CharField()
    content_type = serializers.CharField()
    size_bytes = serializers.IntegerField(min_value=0)


class UploadPlanRequestSerializer(serializers.Serializer):
    provider = EnumField(ProviderEnum)
    user_sub = serializers.CharField()
    project_id = serializers.CharField(required=False, default="default")
    prefix = serializers.CharField()
    file_meta = FileMetaSerializer()


class CompletionPartSerializer(serializers.Serializer):
    PartNumber = serializers.IntegerField(min_value=1)
    ETag = serializers.CharField()


class CompletionPayloadSerializer(serializers.Serializer):
    provider = EnumField(ProviderEnum)
    bucket = serializers.CharField()
    key = serializers.CharField()
    session_id = serializers.CharField()
    mpu_upload_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    parts = CompletionPartSerializer(many=True, required=False)
    checksum = serializers.CharField(required=False, allow_blank=True)


class UploadPlanResponseSerializer(serializers.Serializer):
    upload_type = EnumField(UploadType)
    upload_id = serializers.CharField()
    bucket = serializers.CharField()
    key = serializers.CharField()
    part_size = serializers.IntegerField(required=False, allow_null=True)
    total_parts = serializers.IntegerField(required=False, allow_null=True)
    put_url = serializers.CharField(required=False, allow_null=True)
    part_urls = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )
    complete_url_payload = serializers.DictField(required=False, allow_null=True)


class DownloadRequestSerializer(serializers.Serializer):
    provider = EnumField(ProviderEnum)
    bucket = serializers.CharField(required=False, allow_blank=True)
    key = serializers.CharField()
    expires = serializers.IntegerField(required=False, min_value=60, default=900)
