"""
Teacher URL Configuration

URL prefix: /teacher/
All URLs in this file require the teacher role.
"""

from django.urls import path
from . import views
from accounts.views import TeacherProfileUpdateView

app_name = 'teacher'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.TeacherDashboardView.as_view(), name='dashboard'),

    # Profile
    path('profile/', TeacherProfileUpdateView.as_view(), name='profile'),

    # Company Management
    path('companies/', views.CompanyListView.as_view(), name='companies'),
    path('company/add/', views.CompanyCreateView.as_view(), name='company_add'),
    path('company/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),
    path('company/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    path('api/supervisor/<int:supervisor_id>/', views.get_supervisor_details, name='supervisor_details'),

    # Student Management
    path('students/', views.StudentListView.as_view(), name='students'),
    path('student/add/', views.StudentCreateView.as_view(), name='student_add'),
    path('student/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('student/<int:pk>/reset-password/', views.StudentResetPasswordView.as_view(), name='student_reset_password'),

    # Student Assignment Management
    path('assign/', views.AssignStudentView.as_view(), name='assign_student'),
    path('assignment/<int:pk>/edit/', views.EditAssignmentView.as_view(), name='edit_assignment'),
    path('assignment/<int:pk>/delete/', views.DeleteAssignmentView.as_view(), name='delete_assignment'),

    # Student DTR Viewing
    path('student/<int:student_id>/dtr/', views.StudentDTRView.as_view(), name='student_dtr'),

    # Journal Management
    path('journals/', views.JournalListView.as_view(), name='journals'),
    path('journal/<int:pk>/review/', views.JournalReviewView.as_view(), name='journal_review'),

    # Evaluations
    path('evaluations/', views.EvaluationListView.as_view(), name='evaluations'),
]
