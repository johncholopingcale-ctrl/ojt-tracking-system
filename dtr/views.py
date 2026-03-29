"""
DTR Views - Student Views for Daily Time Record Management

OOP Concept Demonstrated: CLASS-BASED VIEWS WITH FILE HANDLING (TOPIC 7)
=======================================================================
This file demonstrates:
1. File handling: Processing webcam selfie uploads
2. Inheritance: Views inherit from mixins and generic views
3. CRUD operations: Create, Read, Update, Delete DTR logs

CRUD Operations (Topic 10):
- CREATE: DTRLogCreateView - creates new DTR records
- READ: DTRListView - reads/displays DTR records
- UPDATE: DTREditView - updates existing DTR records
- DELETE: DTRDeleteView - deletes DTR records
=======================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum

from accounts.mixins import StudentRequiredMixin
from accounts.utils import FileHandler
from accounts.views import ProfileUpdateView
from .models import DTRLog
from .forms import DTRLogForm, DTREditForm, DTRLogInForm, DTRLogOutForm
from companies.models import Assignment
from journals.models import Journal
from evaluations.models import Evaluation
from django.contrib.auth import get_user_model

from ojt_project.exceptions import OJTValidationError

User = get_user_model()


class StudentDashboardView(StudentRequiredMixin, TemplateView):
    """
    Student's main dashboard showing OJT progress.

    OOP Concept: DASHBOARD VIEW
    --------------------------
    This view aggregates data from multiple models to show
    the student's OJT progress at a glance.

    CRUD Operation: READ - Reading from multiple models
    """

    template_name = 'student/dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Prepare student dashboard context.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        We override get_context_data() to add student-specific data.
        This method demonstrates how objects can aggregate data from
        related objects.
        """
        context = super().get_context_data(**kwargs)
        student = self.request.user

        # Get active assignment
        assignment = Assignment.objects.filter(student=student).first()
        context['assignment'] = assignment

        # Calculate total rendered hours
        total_hours = DTRLog.objects.filter(
            student=student
        ).aggregate(total=Sum('hours_rendered'))['total'] or 0
        context['total_hours'] = total_hours

        # Calculate progress percentage
        required_hours = assignment.required_hours if assignment else 486
        context['required_hours'] = required_hours
        context['progress_percentage'] = min((total_hours / required_hours) * 100, 100) if required_hours > 0 else 0

        # Get company and supervisor info
        if assignment:
            context['company'] = assignment.company
            context['supervisor'] = assignment.company.supervisor

        # Journal statistics
        journals = Journal.objects.filter(student=student)
        context['journal_stats'] = {
            'total': journals.count(),
            'pending': journals.filter(status='pending').count(),
            'approved': journals.filter(status='approved').count(),
            'rejected': journals.filter(status='rejected').count(),
        }

        # Recent DTR logs
        context['recent_dtr'] = DTRLog.objects.filter(
            student=student
        ).order_by('-date')[:5]

        # Recent evaluations
        context['evaluations'] = Evaluation.objects.filter(
            student=student
        ).order_by('-created_at')[:3]

        return context


class DTRListView(StudentRequiredMixin, ListView):
    """
    View student's own DTR logs.

    OOP Concept: LISTVIEW WITH OWNERSHIP FILTERING
    ---------------------------------------------
    This view demonstrates data isolation - students can ONLY
    see their own DTR logs.

    CRUD Operation: READ - Reading student's own DTR records
    """

    model = DTRLog
    template_name = 'student/dtr_list.html'
    context_object_name = 'dtr_logs'
    paginate_by = 20

    def get_queryset(self):
        """
        Get only the current student's DTR logs.

        OOP Concept: DATA ISOLATION
        --------------------------
        Students can only see their OWN data.
        This is enforced at the queryset level.
        """
        return DTRLog.objects.filter(
            student=self.request.user
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        """Add statistics to context."""
        context = super().get_context_data(**kwargs)

        # Total hours
        context['total_hours'] = self.get_queryset().aggregate(
            total=Sum('hours_rendered')
        )['total'] or 0

        return context


class DTRLogCreateView(StudentRequiredMixin, CreateView):
    """
    Create a new DTR log entry with selfie capture.

    OOP Concept: FILE HANDLING IN VIEWS (TOPIC 7)
    -------------------------------------------
    This view demonstrates file handling:
    1. Receiving base64 image data from JavaScript
    2. Converting to a file using FileHandler class
    3. Saving to the model's ImageField

    CRUD Operation: CREATE - Creating new DTR record
    """

    model = DTRLog
    form_class = DTRLogForm
    template_name = 'student/dtr_log.html'
    success_url = reverse_lazy('student:dtr_list')

    def get_form(self, form_class=None):
        """
        Set the student on the form instance before validation.
        This ensures the student is available during model clean().
        """
        form = super().get_form(form_class)
        form.instance.student = self.request.user
        return form

    def form_valid(self, form):
        """
        Handle form submission with selfie processing.

        OOP Concept: FILE HANDLING
        -------------------------
        This method demonstrates:
        1. Reading base64 data from the form
        2. Converting it to a file using FileHandler
        3. Saving to the model

        Exception Handling: Wrapped in try-except
        """
        try:
            # Set the student to current user
            form.instance.student = self.request.user

            # Process selfie from base64 data
            selfie_data = form.cleaned_data.get('selfie_data') or self.request.POST.get('selfie_data')

            if selfie_data and selfie_data.startswith('data:image'):
                # Use FileHandler to convert base64 to file
                selfie_file = FileHandler.save_base64_image(selfie_data, 'selfie')
                form.instance.selfie = selfie_file
            elif not form.instance.selfie:
                messages.error(self.request, "Please capture a selfie before submitting.")
                return self.form_invalid(form)

            response = super().form_valid(form)
            messages.success(self.request, "DTR logged successfully!")
            return response

        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error processing selfie: {str(e)}")
            return self.form_invalid(form)


class DTRLogInView(StudentRequiredMixin, CreateView):
    """
    Log in (time_in) - Create new DTR entry with selfie.
    
    OOP Concept: SEPARATION OF CONCERNS
    ----------------------------------
    Separate view for logging in vs logging out.
    
    CRUD Operation: CREATE - Creating new DTR record with time_in only
    """
    
    model = DTRLog
    form_class = DTRLogInForm
    template_name = 'student/dtr_log_in.html'
    success_url = reverse_lazy('student:dtr_list')
    
    def get_form(self, form_class=None):
        """Set the student on the form instance."""
        form = super().get_form(form_class)
        form.instance.student = self.request.user
        return form
    
    def form_valid(self, form):
        """Handle log-in with selfie processing."""
        try:
            # Set the student to current user
            form.instance.student = self.request.user
            
            # Check if student already logged in today
            today_log = DTRLog.objects.filter(
                student=self.request.user,
                date=form.instance.date
            ).first()
            
            if today_log:
                messages.error(self.request, f"You already logged in on {form.instance.date}. Please log out instead.")
                return self.form_invalid(form)
            
            # Process selfie from base64 data
            selfie_data = form.cleaned_data.get('selfie_data') or self.request.POST.get('selfie_data')
            
            if selfie_data and selfie_data.startswith('data:image'):
                # Use FileHandler to convert base64 to file
                selfie_file = FileHandler.save_base64_image(selfie_data, 'selfie')
                form.instance.selfie = selfie_file
            elif not form.instance.selfie:
                messages.error(self.request, "Please capture a selfie before submitting.")
                return self.form_invalid(form)
            
            response = super().form_valid(form)
            messages.success(self.request, "Logged in successfully! Don't forget to log out later.")
            return response
            
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error processing selfie: {str(e)}")
            return self.form_invalid(form)


class DTRLogOutView(StudentRequiredMixin, UpdateView):
    """
    Log out (time_out) - Update today's DTR entry.
    
    OOP Concept: SEPARATION OF CONCERNS
    ----------------------------------
    Separate view for logging out.
    
    CRUD Operation: UPDATE - Updating DTR record with time_out
    """
    
    model = DTRLog
    form_class = DTRLogOutForm
    template_name = 'student/dtr_log_out.html'
    success_url = reverse_lazy('student:dtr_list')
    
    def get_object(self, queryset=None):
        """Get today's DTR entry for the student."""
        from datetime import date
        try:
            return DTRLog.objects.get(
                student=self.request.user,
                date=date.today()
            )
        except DTRLog.DoesNotExist:
            return None
    
    def get(self, request, *args, **kwargs):
        """Check if there's a log-in entry to log out from."""
        self.object = self.get_object()
        if not self.object:
            messages.error(request, "You haven't logged in today. Please log in first.")
            return redirect('student:dtr_log_in')
        if self.object.time_out:
            messages.warning(request, f"You already logged out today at {self.object.get_time_out_formatted()}.")
            return redirect('student:dtr_list')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle log-out submission."""
        self.object = self.get_object()
        if not self.object:
            messages.error(request, "You haven't logged in today. Please log in first.")
            return redirect('student:dtr_log_in')
        if self.object.time_out:
            messages.warning(request, "You already logged out today.")
            return redirect('student:dtr_list')
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle log-out with success message."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, f"Logged out successfully! Total hours: {self.object.get_hours_rendered()}")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class DTREditView(StudentRequiredMixin, UpdateView):
    """
    Edit an existing DTR log.

    OOP Concept: OWNERSHIP ENFORCEMENT
    ---------------------------------
    Students can only edit their OWN DTR logs.

    CRUD Operation: UPDATE - Updating DTR record
    """

    model = DTRLog
    form_class = DTREditForm
    template_name = 'student/dtr_edit.html'
    success_url = reverse_lazy('student:dtr_list')

    def get_queryset(self):
        """Limit to current student's logs only."""
        return DTRLog.objects.filter(student=self.request.user)

    def form_valid(self, form):
        """Handle edit with success message."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, "DTR log updated successfully!")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class DTRDeleteView(StudentRequiredMixin, DeleteView):
    """
    Delete a DTR log.

    OOP Concept: OWNERSHIP ENFORCEMENT
    ---------------------------------
    Students can only delete their OWN DTR logs.

    CRUD Operation: DELETE - Deleting DTR record
    """

    model = DTRLog
    template_name = 'student/dtr_delete.html'
    success_url = reverse_lazy('student:dtr_list')

    def get_queryset(self):
        """Limit to current student's logs only."""
        return DTRLog.objects.filter(student=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Delete with success message."""
        messages.success(request, "DTR log deleted successfully.")
        return super().delete(request, *args, **kwargs)


class StudentJournalListView(StudentRequiredMixin, ListView):
    """
    View student's own journals.

    CRUD Operation: READ - Reading student's own journals
    """

    model = Journal
    template_name = 'student/journal_list.html'
    context_object_name = 'journals'
    paginate_by = 20

    def get_queryset(self):
        """Get only current student's journals."""
        return Journal.objects.filter(
            student=self.request.user
        ).order_by('-submitted_at')


class StudentEvaluationListView(StudentRequiredMixin, ListView):
    """
    View evaluations received by the student.

    CRUD Operation: READ - Reading evaluations
    """

    model = Evaluation
    template_name = 'student/evaluation_list.html'
    context_object_name = 'evaluations'
    paginate_by = 20

    def get_queryset(self):
        """Get only evaluations for current student."""
        return Evaluation.objects.filter(
            student=self.request.user
        ).order_by('-created_at')
