"""
Student URL Configuration

URL prefix: /student/
All URLs in this file require the student role.
"""

from django.urls import path
from . import views
from journals.views import JournalCreateView, JournalEditView, JournalDeleteView
from accounts.views import ProfileUpdateView

app_name = 'student'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.StudentDashboardView.as_view(), name='dashboard'),

    # DTR Management
    path('dtr/', views.DTRListView.as_view(), name='dtr_list'),
    path('dtr/log-in/', views.DTRLogInView.as_view(), name='dtr_log_in'),
    path('dtr/log-out/', views.DTRLogOutView.as_view(), name='dtr_log_out'),
    # path('dtr/log/', views.DTRLogCreateView.as_view(), name='dtr_log'),  # DEPRECATED: Use log-in and log-out separately
    path('dtr/<int:pk>/edit/', views.DTREditView.as_view(), name='dtr_edit'),
    path('dtr/<int:pk>/delete/', views.DTRDeleteView.as_view(), name='dtr_delete'),

    # Journal Management
    path('journals/', views.StudentJournalListView.as_view(), name='journal_list'),
    path('journal/submit/', JournalCreateView.as_view(), name='journal_submit'),
    path('journal/<int:pk>/edit/', JournalEditView.as_view(), name='journal_edit'),
    path('journal/<int:pk>/delete/', JournalDeleteView.as_view(), name='journal_delete'),

    # Evaluations
    path('evaluations/', views.StudentEvaluationListView.as_view(), name='evaluations'),

    # Profile
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
]
