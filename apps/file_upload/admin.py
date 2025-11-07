from django.contrib import admin
from apps.file_upload.models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin interface for FileUpload model."""
    list_display = ['id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


