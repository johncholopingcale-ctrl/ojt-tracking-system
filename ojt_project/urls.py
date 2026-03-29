"""
OJT Project URL Configuration

OOP Concept Demonstrated: Routing and Delegation
URL configuration demonstrates the delegation pattern where requests are routed
to appropriate view classes based on URL patterns. Each app has its own urls.py
following the Single Responsibility Principle.

SOLID Principle - Open/Closed: New URL patterns can be added without modifying existing ones.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_redirect(request):
    """
    Redirect users to their role-specific dashboard or login page.

    OOP Concept: Polymorphic Behavior
    This function demonstrates polymorphic behavior - the same URL (/) returns
    different responses based on the user's authentication status and role.
    """
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return redirect('accounts:login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('teacher/', include('companies.urls_teacher', namespace='teacher')),
    path('student/', include('dtr.urls_student', namespace='student')),
    path('supervisor/', include('evaluations.urls_supervisor', namespace='supervisor')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
