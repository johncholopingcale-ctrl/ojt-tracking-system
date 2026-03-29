"""
Journals Admin Configuration
"""

from django.contrib import admin
from .models import Journal


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    """Admin configuration for Journal model."""

    list_display = ('student', 'week_number', 'status', 'submitted_at', 'updated_at')
    list_filter = ('status', 'submitted_at', 'week_number')
    search_fields = ('student__username', 'student__first_name', 'content')
    readonly_fields = ('submitted_at', 'created_at', 'updated_at')
    date_hierarchy = 'submitted_at'

    fieldsets = (
        ('Journal Information', {
            'fields': ('student', 'week_number', 'content')
        }),
        ('Review', {
            'fields': ('status', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
