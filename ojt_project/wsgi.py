"""
WSGI config for ojt_project.

OOP Concept: Application Gateway Pattern
WSGI (Web Server Gateway Interface) demonstrates how object-oriented web applications
communicate with web servers through a standardized interface.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ojt_project.settings')

application = get_wsgi_application()
