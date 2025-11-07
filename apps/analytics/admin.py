from django.contrib import admin
from apps.analytics.models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """Admin interface for AnalyticsEvent model."""
    list_display = ['id', 'event_type', 'user_id', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['event_type', 'user_id']
    readonly_fields = ['created_at']


