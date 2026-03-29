"""
Accounts Admin Configuration

OOP Concept: ADMIN CUSTOMIZATION THROUGH INHERITANCE
===================================================
Django admin classes inherit from ModelAdmin and override
methods/attributes to customize the admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for User model.

    OOP Concept: INHERITANCE FROM USERADMIN
    --------------------------------------
    We inherit from UserAdmin (not just ModelAdmin) to get
    all the special user handling like password hashing.
    """

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Add role to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('OJT Information', {
            'fields': ('role', 'phone', 'department', 'profile_pic')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('OJT Information', {
            'fields': ('role', 'phone', 'department')
        }),
    )
