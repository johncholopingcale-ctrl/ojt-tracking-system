"""
DTR Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import DTRLog, DTRHistory


@admin.register(DTRLog)
class DTRLogAdmin(admin.ModelAdmin):
    """Admin configuration for DTRLog model."""

    list_display = ('student', 'date', 'time_in', 'time_out', 'hours_rendered', 'confirmation_status', 'selfie_thumbnail')
    list_filter = ('date', 'student', 'confirmation_status')
    search_fields = ('student__username', 'student__first_name', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('hours_rendered', 'selfie_preview', 'logout_selfie_preview')

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
    selfie_preview.short_description = 'Login Selfie Preview'

    def logout_selfie_preview(self, obj):
        """Display larger logout selfie in detail view."""
        if obj.logout_selfie:
            return format_html('<img src="{}" height="200" />', obj.logout_selfie.url)
        return "No logout selfie"
    logout_selfie_preview.short_description = 'Logout Selfie Preview'


@admin.register(DTRHistory)
class DTRHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for DTRHistory model."""

    list_display = ('student', 'date', 'hours_rendered', 'confirmation_status', 'archived_at', 'archived_reason')
    list_filter = ('date', 'confirmation_status', 'archived_reason', 'archived_at')
    search_fields = ('student__username', 'student__first_name', 'notes', 'confirmation_remarks')
    date_hierarchy = 'date'
    readonly_fields = ('selfie_preview', 'logout_selfie_preview', 'archived_at')

    def selfie_preview(self, obj):
        """Display larger selfie in detail view."""
        if obj.selfie:
            return format_html('<img src="{}" height="200" />', obj.selfie.url)
        return "No selfie"
    selfie_preview.short_description = 'Login Selfie Preview'

    def logout_selfie_preview(self, obj):
        """Display larger logout selfie in detail view."""
        if obj.logout_selfie:
            return format_html('<img src="{}" height="200" />', obj.logout_selfie.url)
        return "No logout selfie"
    logout_selfie_preview.short_description = 'Logout Selfie Preview'
