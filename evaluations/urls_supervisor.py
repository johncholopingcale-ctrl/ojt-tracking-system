"""
Supervisor URL Configuration

URL prefix: /supervisor/
All URLs in this file require the supervisor role.
"""

from django.urls import path
from . import views
from accounts.views import SupervisorProfileUpdateView

app_name = 'supervisor'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.SupervisorDashboardView.as_view(), name='dashboard'),

    # Profile
    path('profile/', SupervisorProfileUpdateView.as_view(), name='profile'),

    # Intern Management
    path('interns/', views.InternListView.as_view(), name='intern_list'),
    path('intern/<int:student_id>/dtr/', views.InternDTRView.as_view(), name='intern_dtr'),

    # DTR Confirmation
    path('dtr/pending/', views.PendingDTRListView.as_view(), name='pending_dtr'),
    path('dtr/<int:pk>/confirm/', views.DTRConfirmationView.as_view(), name='dtr_confirm'),

    # Evaluation Management
    path('evaluation/add/<int:student_id>/', views.EvaluationCreateView.as_view(), name='evaluation_add'),
    path('evaluation/<int:pk>/edit/', views.EvaluationEditView.as_view(), name='evaluation_edit'),
    path('evaluation/<int:pk>/delete/', views.EvaluationDeleteView.as_view(), name='evaluation_delete'),
]
