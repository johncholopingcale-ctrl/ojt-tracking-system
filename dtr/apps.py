"""DTR App Configuration"""

from django.apps import AppConfig


class DtrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dtr'
    verbose_name = 'Daily Time Records'
