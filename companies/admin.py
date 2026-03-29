"""
Companies Admin Configuration
"""

from django.contrib import admin
from .models import Company, Assignment


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin configuration for Company model."""

    list_display = ('name', 'supervisor', 'contact_email', 'contact_phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'address', 'supervisor__username')
    raw_id_fields = ('supervisor',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for Assignment model."""

    list_display = ('student', 'company', 'start_date', 'end_date', 'required_hours')
    list_filter = ('company', 'start_date', 'end_date')
    search_fields = ('student__username', 'student__first_name', 'company__name')
    raw_id_fields = ('student', 'company')
    date_hierarchy = 'start_date'
