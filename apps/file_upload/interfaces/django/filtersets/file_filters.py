from __future__ import annotations
from django_filters import rest_framework as filters


class FileUploadFilter(filters.FilterSet):
    user_sub = filters.CharFilter(field_name="user__pk", lookup_expr="exact")
    status = filters.CharFilter(field_name="status", lookup_expr="exact")
    created_after = filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    ordering = filters.OrderingFilter(
        fields=(("created_at", "created_at"), ("status", "status")),
        field_labels={"created_at": "Created at", "status": "Status"},
    )
