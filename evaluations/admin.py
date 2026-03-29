"""
Evaluations Admin Configuration
"""

from django.contrib import admin
from .models import Evaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin configuration for Evaluation model."""

    list_display = ('student', 'supervisor', 'work_quality', 'attitude', 'overall_rating', 'recommendation', 'created_at')
    list_filter = ('recommendation', 'created_at', 'work_quality', 'attitude')
    search_fields = ('student__username', 'supervisor__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
