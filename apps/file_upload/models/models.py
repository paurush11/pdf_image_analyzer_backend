from django.db import models


class FileUpload(models.Model):
    """Model for file uploads."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'file_uploads'

