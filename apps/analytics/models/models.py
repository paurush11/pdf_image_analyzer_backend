from django.db import models


class AnalyticsEvent(models.Model):
    """Model for analytics events."""
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    user_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_events'

