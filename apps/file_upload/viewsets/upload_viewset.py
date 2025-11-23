# apps/file_upload/interfaces/django/viewsets/upload_viewset.py
from __future__ import annotations
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from apps.file_upload.serializers import (
    UploadPlanRequestSerializer,
    UploadPlanResponseSerializer,
    CompletionPayloadSerializer,
    DownloadRequestSerializer,
)
from apps.file_upload.domain.models.dto import (
    UploadCtx,
    FileMeta,
    CompletionPayload,
    DownloadCtx,
)
from apps.file_upload.application.services.file_service import get_file_service


class UploadViewSet(ViewSet):
    def __init__(self):
        self.file_service = get_file_service()

    def plan(self, request: Request):
        ser = UploadPlanRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        ctx = UploadCtx(
            provider=d["provider"],  # Enum
            user_sub=(
                str(request.user.pk) if request.user.is_authenticated else d["user_sub"]
            ),
            project_id=d.get("project_id", "default"),
            prefix=d["prefix"],
            file_meta=FileMeta(**d["file_meta"]),
        )
        plan = self.file_service.plan_upload(ctx)

        out = UploadPlanResponseSerializer(
            {
                "upload_type": plan.upload_type,  # Enum—Serializer handles to_representation
                "upload_id": plan.upload_id,
                "bucket": plan.bucket,
                "key": plan.key,
                "part_size": plan.part_size,
                "total_parts": plan.total_parts,
                "put_url": plan.put_url,
                "part_urls": plan.part_urls,
                "complete_url_payload": plan.complete_url_payload,
            }
        ).data
        return Response(out, status=status.HTTP_200_OK)

    def complete(self, request):
        ser = CompletionPayloadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payload = CompletionPayload(**ser.validated_data)
        self.file_service.complete_upload(payload)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    def presign_download(self, request):
        ser = DownloadRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        url = self.file_service.presign_download(
            DownloadCtx(
                provider=d["provider"], bucket=d.get("bucket", ""), key=d["key"]
            )
        )
        return Response({"url": url}, status=status.HTTP_200_OK)
