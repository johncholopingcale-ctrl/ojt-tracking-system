"""
Accounts URL Configuration

OOP Concept: URL ROUTING AND DELEGATION
======================================
URL patterns demonstrate the delegation pattern - each URL is
mapped to a view class that handles the request.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
