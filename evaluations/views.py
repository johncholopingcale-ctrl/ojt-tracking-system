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

        # Get pending DTR confirmations count
        student_ids = assignments.values_list('student_id', flat=True)
        pending_dtr_count = DTRLog.objects.filter(
            student_id__in=student_ids,
            confirmation_status='pending'
        ).count()
        context['pending_dtr_count'] = pending_dtr_count

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
        """Get assignments for supervisor's companies."""
        supervisor = self.request.user
        companies = Company.objects.filter(supervisor=supervisor)
        return Assignment.objects.filter(company__in=companies).order_by('-start_date')


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
        context['student'] = get_object_or_404(User, pk=student_id, role='student')
        context['total_hours'] = self.get_queryset().aggregate(
            total=Sum('hours_rendered')
        )['total'] or 0
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
    View for supervisors to confirm or reject a DTR log.

    OOP Concept: PERMISSION-CHECKED CONFIRMATION
    -------------------------------------------
    Verifies supervisor can confirm/reject this student's DTR.

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
        return context

    def post(self, request, *args, **kwargs):
        """Handle confirmation or rejection."""
        from django.utils import timezone

        remarks = request.POST.get('remarks', '')
        action = request.POST.get('action')

        if action == 'confirm':
            self.dtr_log.confirmation_status = 'confirmed'
            self.dtr_log.confirmed_by = request.user
            self.dtr_log.confirmed_at = timezone.now()
            self.dtr_log.confirmation_remarks = remarks
            self.dtr_log.save()
            messages.success(request, f"DTR log for {self.dtr_log.date} has been confirmed.")

        elif action == 'reject':
            if not remarks:
                messages.error(request, "Please provide remarks when rejecting a DTR log.")
                return self.get(request, *args, **kwargs)

            self.dtr_log.confirmation_status = 'rejected'
            self.dtr_log.confirmed_by = request.user
            self.dtr_log.confirmed_at = timezone.now()
            self.dtr_log.confirmation_remarks = remarks
            self.dtr_log.save()
            messages.warning(request, f"DTR log for {self.dtr_log.date} has been rejected.")

        return redirect('supervisor:intern_dtr', student_id=self.dtr_log.student.pk)


class PendingDTRListView(SupervisorRequiredMixin, ListView):
    """
    List all pending DTR logs from interns at supervisor's companies.

    OOP Concept: FILTERED LISTVIEW
    -----------------------------
    Shows only pending confirmations for supervisor's interns.

    CRUD Operation: READ
    """

    model = DTRLog
    template_name = 'supervisor/pending_dtr_list.html'
    context_object_name = 'dtr_logs'
    paginate_by = 20

    def get_queryset(self):
        """Get pending DTR logs for supervisor's interns."""
        supervisor = self.request.user
        companies = Company.objects.filter(supervisor=supervisor)
        student_ids = Assignment.objects.filter(
            company__in=companies
        ).values_list('student_id', flat=True)

        return DTRLog.objects.filter(
            student_id__in=student_ids,
            confirmation_status='pending'
        ).order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = self.get_queryset().count()
        return context
