from django.db import models


class Job(models.Model):
    """Model for job tracking."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    job_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'jobs'

