"""
ASGI config for ojt_project.

OOP Concept: Asynchronous Gateway Pattern
ASGI (Asynchronous Server Gateway Interface) extends WSGI to support async operations,
demonstrating how OOP applications can handle concurrent requests.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ojt_project.settings')

application = get_asgi_application()
