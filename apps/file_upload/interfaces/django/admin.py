from django.contrib import admin

try:
    from apps.file_upload import models

    admin.site.register(models.UploadBatch)
    admin.site.register(models.File)
except Exception:
    pass
