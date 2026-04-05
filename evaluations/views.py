"""
Evaluations Views - Supervisor Views for Intern Evaluation

OOP Concept Demonstrated: VIEWS WITH DATA FILTERING
=================================================
These views demonstrate:
1. Role-based access control through mixins
2. Data filtering based on supervisor's assigned companies
3. CRUD operations for evaluations
"""

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count

from accounts.mixins import SupervisorRequiredMixin
from .models import Evaluation
from .forms import EvaluationForm
from companies.models import Company, Assignment
from dtr.models import DTRLog
from django.contrib.auth import get_user_model

from ojt_project.exceptions import OJTValidationError, OJTPermissionError

User = get_user_model()


class SupervisorDashboardView(SupervisorRequiredMixin, TemplateView):
    """
    Supervisor's main dashboard.

    OOP Concept: DASHBOARD WITH COMPUTED DATA
    ----------------------------------------
    Aggregates data from multiple sources.
    Shows separate counts for pending logins and logouts.
    """

    template_name = 'supervisor/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supervisor = self.request.user

        # Get companies supervised by this user
        companies = Company.objects.filter(supervisor=supervisor)
        context['companies'] = companies

        # Get assigned interns
        assignments = Assignment.objects.filter(company__in=companies)
        context['intern_count'] = assignments.values('student').distinct().count()

        # Get evaluations given by this supervisor
        evaluations = Evaluation.objects.filter(supervisor=supervisor)
        context['evaluation_count'] = evaluations.count()

        # Get student IDs for filtering
        student_ids = assignments.values_list('student_id', flat=True)
        
        # NEW: Separate counts for login and logout confirmations
        pending_login_count = DTRLog.objects.filter(
            student_id__in=student_ids,
            login_confirmation_status='pending'
        ).count()
        context['pending_login_count'] = pending_login_count
        
        pending_logout_count = DTRLog.objects.filter(
            student_id__in=student_ids,
            time_out__isnull=False,  # Only count if they've actually logged out
            logout_confirmation_status='pending'
        ).count()
        context['pending_logout_count'] = pending_logout_count
        
        # Total pending (for backward compatibility)
        context['pending_dtr_count'] = pending_login_count + pending_logout_count

        # Get resubmitted DTR count (pending resubmissions needing review)
        resubmitted_dtr_count = DTRLog.objects.filter(
            student_id__in=student_ids,
            login_confirmation_status='pending',
            is_resubmission=True
        ).count()
        context['resubmitted_dtr_count'] = resubmitted_dtr_count

        # Get list of interns with their hours
        interns_data = []
        for assignment in assignments:
            total_hours = DTRLog.objects.filter(
                student=assignment.student,
                date__gte=assignment.start_date,
                date__lte=assignment.end_date
            ).aggregate(total=Sum('hours_rendered'))['total'] or 0

            interns_data.append({
                'assignment': assignment,
                'student': assignment.student,
                'company': assignment.company,
                'total_hours': total_hours,
                'has_evaluation': evaluations.filter(student=assignment.student).exists()
            })

        context['interns'] = interns_data

        return context


class InternListView(SupervisorRequiredMixin, ListView):
    """
    List all interns assigned to supervisor's companies.

    CRUD Operation: READ
    """

    template_name = 'supervisor/intern_list.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        """Get assignments for supervisor's companies with latest DTR info."""
        from dtr.models import DTRLog
        from django.db.models import Max, Q
        
        supervisor = self.request.user
        companies = Company.objects.filter(supervisor=supervisor)
        assignments = Assignment.objects.filter(company__in=companies).order_by('-start_date')
        
        # Annotate each assignment with latest DTR date and status
        for assignment in assignments:
            latest_dtr = DTRLog.objects.filter(
                student=assignment.student
            ).order_by('-date').first()
            
            assignment.latest_login_date = latest_dtr.date if latest_dtr else None
            
            # Determine the current status based on confirmation workflow
            if latest_dtr:
                if latest_dtr.login_confirmation_status == 'pending':
                    assignment.login_status = 'pending_login'
                elif latest_dtr.login_confirmation_status == 'rejected':
                    assignment.login_status = 'rejected_login'
                elif latest_dtr.login_confirmation_status == 'confirmed' and not latest_dtr.time_out:
                    assignment.login_status = 'logged_in'
                elif latest_dtr.time_out and latest_dtr.logout_confirmation_status == 'pending':
                    assignment.login_status = 'pending_logout'
                elif latest_dtr.time_out and latest_dtr.logout_confirmation_status == 'rejected':
                    assignment.login_status = 'rejected_logout'
                elif latest_dtr.time_out and latest_dtr.logout_confirmation_status == 'confirmed':
                    assignment.login_status = 'logged_out'
                else:
                    assignment.login_status = 'unknown'
            else:
                assignment.login_status = 'no_dtr'
        
        return assignments


class InternDTRView(SupervisorRequiredMixin, ListView):
    """
    View DTR logs for a specific intern.

    OOP Concept: PERMISSION-BASED DATA ACCESS
    ----------------------------------------
    Supervisor can only see DTR of interns at their company.

    CRUD Operation: READ
    """

    model = DTRLog
    template_name = 'supervisor/intern_dtr.html'
    context_object_name = 'dtr_logs'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        """Verify supervisor has access to this student."""
        student_id = self.kwargs.get('student_id')
        supervisor = request.user

        # Check if student is at supervisor's company
        companies = Company.objects.filter(supervisor=supervisor)
        has_access = Assignment.objects.filter(
            student_id=student_id,
            company__in=companies
        ).exists()

        if not has_access:
            messages.error(request, "You don't have access to this student's records.")
            return redirect('supervisor:dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return DTRLog.objects.filter(
            student_id=student_id
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_id')
        queryset = self.get_queryset()
        
        context['student'] = get_object_or_404(User, pk=student_id, role='student')
        context['total_hours'] = queryset.aggregate(
            total=Sum('hours_rendered')
        )['total'] or 0
        
        # Pending counts for this student
        context['pending_login_count'] = queryset.filter(
            login_confirmation_status='pending'
        ).count()
        context['pending_logout_count'] = queryset.filter(
            logout_confirmation_status='pending',
            time_out__isnull=False
        ).count()
        
        return context


class EvaluationCreateView(SupervisorRequiredMixin, CreateView):
    """
    Create evaluation for an intern.

    OOP Concept: PERMISSION-CHECKED CREATE
    ------------------------------------
    Verifies supervisor can evaluate this student.

    CRUD Operation: CREATE
    """

    model = Evaluation
    form_class = EvaluationForm
    template_name = 'supervisor/evaluation_add.html'
    success_url = reverse_lazy('supervisor:dashboard')

    def dispatch(self, request, *args, **kwargs):
        """Verify supervisor can evaluate this student."""
        student_id = self.kwargs.get('student_id')
        supervisor = request.user

        # Check if student is at supervisor's company
        companies = Company.objects.filter(supervisor=supervisor)
        has_access = Assignment.objects.filter(
            student_id=student_id,
            company__in=companies
        ).exists()

        if not has_access:
            messages.error(request, "You can only evaluate students at your company.")
            return redirect('supervisor:dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_id')
        context['student'] = get_object_or_404(User, pk=student_id, role='student')
        return context

    def get_form(self, form_class=None):
        """Set supervisor and student on the form instance before validation."""
        form = super().get_form(form_class)
        form.instance.supervisor = self.request.user
        form.instance.student_id = self.kwargs.get('student_id')
        return form

    def form_valid(self, form):
        """Handle successful form submission."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Evaluation submitted successfully!")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class EvaluationEditView(SupervisorRequiredMixin, UpdateView):
    """
    Edit an existing evaluation.

    CRUD Operation: UPDATE
    """

    model = Evaluation
    form_class = EvaluationForm
    template_name = 'supervisor/evaluation_edit.html'
    success_url = reverse_lazy('supervisor:dashboard')

    def get_queryset(self):
        """Limit to evaluations by this supervisor."""
        return Evaluation.objects.filter(supervisor=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Evaluation updated successfully!")
        return response


class EvaluationDeleteView(SupervisorRequiredMixin, DeleteView):
    """
    Delete an evaluation.

    CRUD Operation: DELETE
    """

    model = Evaluation
    template_name = 'supervisor/evaluation_delete.html'
    success_url = reverse_lazy('supervisor:dashboard')

    def get_queryset(self):
        """Limit to evaluations by this supervisor."""
        return Evaluation.objects.filter(supervisor=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Evaluation deleted successfully.")
        return super().delete(request, *args, **kwargs)


class DTRConfirmationView(SupervisorRequiredMixin, TemplateView):
    """
    View for supervisors to confirm or reject a DTR log's login or logout.

    OOP Concept: PERMISSION-CHECKED CONFIRMATION
    -------------------------------------------
    Verifies supervisor can confirm/reject this student's DTR.
    Handles separate login and logout confirmation.

    CRUD Operation: UPDATE - Updating DTR confirmation status
    """

    template_name = 'supervisor/dtr_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        """Verify supervisor has access to this DTR log."""
        dtr_id = self.kwargs.get('pk')
        supervisor = request.user

        # Get the DTR log
        self.dtr_log = get_object_or_404(DTRLog, pk=dtr_id)

        # Check if student is at supervisor's company
        companies = Company.objects.filter(supervisor=supervisor)
        has_access = Assignment.objects.filter(
            student=self.dtr_log.student,
            company__in=companies
        ).exists()

        if not has_access:
            messages.error(request, "You don't have access to confirm this DTR log.")
            return redirect('supervisor:dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dtr_log'] = self.dtr_log
        context['student'] = self.dtr_log.student
        # Add confirmation type context
        context['login_needs_confirm'] = self.dtr_log.is_login_pending()
        context['logout_needs_confirm'] = self.dtr_log.time_out and self.dtr_log.is_logout_pending()
        context['login_confirmed'] = self.dtr_log.is_login_confirmed()
        context['logout_confirmed'] = self.dtr_log.is_logout_confirmed()
        return context

    def post(self, request, *args, **kwargs):
        """Handle confirmation or rejection for login or logout."""
        from django.utils import timezone

        remarks = request.POST.get('remarks', '')
        action = request.POST.get('action')
        confirm_type = request.POST.get('confirm_type', 'login')  # 'login' or 'logout'

        if confirm_type == 'login':
            if action == 'confirm':
                self.dtr_log.login_confirmation_status = 'confirmed'
                self.dtr_log.login_confirmed_by = request.user
                self.dtr_log.login_confirmed_at = timezone.now()
                self.dtr_log.login_remarks = remarks
                self.dtr_log.is_valid = True
                self.dtr_log.save()
                messages.success(request, f"Login for {self.dtr_log.date} has been confirmed. Student can now log out.")

            elif action == 'reject':
                if not remarks:
                    messages.error(request, "Please provide remarks when rejecting a login.")
                    return self.get(request, *args, **kwargs)

                self.dtr_log.login_confirmation_status = 'rejected'
                self.dtr_log.login_confirmed_by = request.user
                self.dtr_log.login_confirmed_at = timezone.now()
                self.dtr_log.login_remarks = remarks
                self.dtr_log.confirmation_status = 'rejected'  # Overall status
                self.dtr_log.is_valid = False
                self.dtr_log.save()
                messages.warning(request, f"Login for {self.dtr_log.date} has been rejected. Student can resubmit.")

        elif confirm_type == 'logout':
            if action == 'confirm':
                self.dtr_log.logout_confirmation_status = 'confirmed'
                self.dtr_log.logout_confirmed_by = request.user
                self.dtr_log.logout_confirmed_at = timezone.now()
                self.dtr_log.logout_remarks = remarks
                
                # If both login and logout are confirmed, mark overall as confirmed
                if self.dtr_log.is_login_confirmed():
                    self.dtr_log.confirmation_status = 'confirmed'
                    self.dtr_log.confirmed_by = request.user
                    self.dtr_log.confirmed_at = timezone.now()
                    self.dtr_log.confirmation_remarks = f"Login: {self.dtr_log.login_remarks or 'OK'}. Logout: {remarks or 'OK'}"
                
                self.dtr_log.save()
                messages.success(request, f"Logout for {self.dtr_log.date} has been confirmed. DTR is now fully approved.")

            elif action == 'reject':
                if not remarks:
                    messages.error(request, "Please provide remarks when rejecting a logout.")
                    return self.get(request, *args, **kwargs)

                self.dtr_log.logout_confirmation_status = 'rejected'
                self.dtr_log.logout_confirmed_by = request.user
                self.dtr_log.logout_confirmed_at = timezone.now()
                self.dtr_log.logout_remarks = remarks
                self.dtr_log.save()
                messages.warning(request, f"Logout for {self.dtr_log.date} has been rejected.")

        return redirect('supervisor:intern_dtr', student_id=self.dtr_log.student.pk)


class PendingDTRListView(SupervisorRequiredMixin, ListView):
    """
    List all pending DTR logs from interns at supervisor's companies.

    OOP Concept: FILTERED LISTVIEW
    -----------------------------
    Shows pending login and logout confirmations separately.

    CRUD Operation: READ
    """

    model = DTRLog
    template_name = 'supervisor/pending_dtr_list.html'
    context_object_name = 'dtr_logs'
    paginate_by = 20

    def get_queryset(self):
        """Get pending DTR logs for supervisor's interns based on filter."""
        from django.db.models import Q
        
        supervisor = self.request.user
        companies = Company.objects.filter(supervisor=supervisor)
        student_ids = Assignment.objects.filter(
            company__in=companies
        ).values_list('student_id', flat=True)

        filter_type = self.request.GET.get('filter', 'login')
        
        base_query = DTRLog.objects.filter(student_id__in=student_ids)
        
        if filter_type == 'login':
            # Pending login confirmations
            return base_query.filter(
                login_confirmation_status='pending'
            ).order_by('-date', '-created_at')
        else:
            # Pending logout confirmations (only where they've actually logged out)
            return base_query.filter(
                time_out__isnull=False,
                logout_confirmation_status='pending'
            ).order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        supervisor = self.request.user
        companies = Company.objects.filter(supervisor=supervisor)
        student_ids = Assignment.objects.filter(
            company__in=companies
        ).values_list('student_id', flat=True)
        
        # Separate counts for login and logout
        context['pending_login_count'] = DTRLog.objects.filter(
            student_id__in=student_ids,
            login_confirmation_status='pending'
        ).count()
        
        context['pending_logout_count'] = DTRLog.objects.filter(
            student_id__in=student_ids,
            time_out__isnull=False,
            logout_confirmation_status='pending'
        ).count()
        
        context['pending_count'] = context['pending_login_count'] + context['pending_logout_count']
        context['current_filter'] = self.request.GET.get('filter', 'login')
        
        # Count resubmissions for highlighting
        context['resubmitted_login_count'] = DTRLog.objects.filter(
            student_id__in=student_ids,
            login_confirmation_status='pending',
            is_resubmission=True
        ).count()
        
        context['resubmitted_logout_count'] = DTRLog.objects.filter(
            student_id__in=student_ids,
            time_out__isnull=False,
            logout_confirmation_status='pending',
            is_resubmission=True
        ).count()
        
        return context
