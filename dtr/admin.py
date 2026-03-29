"""
DTR Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import DTRLog


@admin.register(DTRLog)
class DTRLogAdmin(admin.ModelAdmin):
    """Admin configuration for DTRLog model."""

    list_display = ('student', 'date', 'time_in', 'time_out', 'hours_rendered', 'selfie_thumbnail')
    list_filter = ('date', 'student')
    search_fields = ('student__username', 'student__first_name', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('hours_rendered', 'selfie_preview')

    def selfie_thumbnail(self, obj):
        """Display small selfie thumbnail in list."""
        if obj.selfie:
            return format_html('<img src="{}" height="40" />', obj.selfie.url)
        return "No selfie"
    selfie_thumbnail.short_description = 'Selfie'

    def selfie_preview(self, obj):
        """Display larger selfie in detail view."""
        if obj.selfie:
            return format_html('<img src="{}" height="200" />', obj.selfie.url)
        return "No selfie"
    selfie_preview.short_description = 'Selfie Preview'
