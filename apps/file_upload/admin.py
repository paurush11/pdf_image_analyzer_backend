from django.contrib import admin
from apps.file_upload import models

admin.site.register(models.UploadBatch)
admin.site.register(models.File)
