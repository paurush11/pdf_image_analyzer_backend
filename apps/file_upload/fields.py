# apps/file_upload/interfaces/django/fields.py
from __future__ import annotations
from rest_framework import serializers
from enum import Enum


class EnumField(serializers.ChoiceField):
    def __init__(self, enum: type[Enum], **kwargs):
        self._enum = enum
        choices = [e.value for e in enum]
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data):
        val = super().to_internal_value(data)
        # map string → Enum
        for e in self._enum:
            if e.value == val:
                return e
        raise serializers.ValidationError("Invalid enum value")

    def to_representation(self, obj):
        if isinstance(obj, self._enum):
            return obj.value
        return super().to_representation(obj)
