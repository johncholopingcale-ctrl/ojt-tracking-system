"""
Accounts App Configuration

OOP Concept: APP CONFIGURATION AS A CLASS
=========================================
Django uses a class to configure each app, demonstrating
how configuration can be encapsulated in objects.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration class for the accounts app.

    OOP Concept: CONFIGURATION CLASS
    -------------------------------
    This class inherits from AppConfig and customizes
    the app's name and display label.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User Accounts & Authentication'
