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
from django.db.models import Sum, Q

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

        # Rejected DTR count for warning banner
        context['rejected_dtr_count'] = DTRLog.objects.filter(
            student=student,
            confirmation_status='rejected'
        ).count()

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

        queryset = self.get_queryset()
        
        # Total hours
        context['total_hours'] = queryset.aggregate(
            total=Sum('hours_rendered')
        )['total'] or 0

        # Rejected DTR count for warning banner (either login or logout rejected)
        context['rejected_dtr_count'] = queryset.filter(
            Q(login_confirmation_status='rejected') | Q(logout_confirmation_status='rejected')
        ).count()
        
        # Pending login confirmations
        context['pending_login_count'] = queryset.filter(
            login_confirmation_status='pending'
        ).count()
        
        # Pending logout confirmations
        context['pending_logout_count'] = queryset.filter(
            logout_confirmation_status='pending',
            time_out__isnull=False
        ).count()

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
    Login now requires supervisor confirmation before logout is allowed.
    
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
    
    def get_context_data(self, **kwargs):
        """Add pending login info to context."""
        context = super().get_context_data(**kwargs)
        from datetime import date
        
        # Check if there's already a pending login for today
        today_log = DTRLog.objects.filter(
            student=self.request.user,
            date=date.today()
        ).first()
        
        context['today_log'] = today_log
        if today_log:
            context['has_pending_login'] = today_log.is_login_pending()
            context['login_confirmed'] = today_log.is_login_confirmed()
            context['login_rejected'] = today_log.is_login_rejected()
        
        return context
    
    def form_valid(self, form):
        """Handle log-in with selfie processing. Sets login_confirmation_status to pending."""
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
            
            # Set login confirmation status to pending (requires supervisor approval)
            form.instance.login_confirmation_status = 'pending'
            form.instance.confirmation_status = 'pending'  # Overall status also pending
            
            response = super().form_valid(form)
            messages.success(
                self.request, 
                "Logged in successfully! Your login is pending supervisor confirmation. "
                "You can log out once your supervisor confirms your login."
            )
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
    Login must be confirmed by supervisor before logout is allowed.
    
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
    
    def get_context_data(self, **kwargs):
        """Add login confirmation status to context."""
        context = super().get_context_data(**kwargs)
        if self.object:
            context['login_confirmed'] = self.object.is_login_confirmed()
            context['login_pending'] = self.object.is_login_pending()
            context['login_rejected'] = self.object.is_login_rejected()
            context['can_logout'] = self.object.can_logout()
        return context
    
    def get(self, request, *args, **kwargs):
        """Check if there's a log-in entry to log out from and if login is confirmed."""
        self.object = self.get_object()
        if not self.object:
            messages.error(request, "You haven't logged in today. Please log in first.")
            return redirect('student:dtr_log_in')
        if self.object.time_out:
            messages.warning(request, f"You already logged out today at {self.object.get_time_out_formatted()}.")
            return redirect('student:dtr_list')
        
        # Check if login is confirmed - allow viewing but show message
        if not self.object.is_login_confirmed():
            if self.object.is_login_pending():
                messages.warning(
                    request, 
                    "Your login is pending supervisor confirmation. "
                    "You can log out once your supervisor confirms your login."
                )
            elif self.object.is_login_rejected():
                messages.error(
                    request, 
                    "Your login was rejected by your supervisor. "
                    "Please check the rejection reason and resubmit if needed."
                )
                return redirect('student:dtr_list')
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle log-out submission. Requires login to be confirmed."""
        self.object = self.get_object()
        if not self.object:
            messages.error(request, "You haven't logged in today. Please log in first.")
            return redirect('student:dtr_log_in')
        if self.object.time_out:
            messages.warning(request, "You already logged out today.")
            return redirect('student:dtr_list')
        
        # Require login confirmation before allowing logout
        if not self.object.is_login_confirmed():
            if self.object.is_login_pending():
                messages.error(
                    request, 
                    "Cannot log out yet. Your login must be confirmed by your supervisor first."
                )
            else:
                messages.error(
                    request, 
                    "Cannot log out. Your login was rejected. Please check and resubmit."
                )
            return redirect('student:dtr_list')
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle log-out with selfie processing. Sets logout_confirmation_status to pending."""
        try:
            # Process logout selfie from base64 data
            selfie_data = form.cleaned_data.get('selfie_data') or self.request.POST.get('selfie_data')
            
            if selfie_data and selfie_data.startswith('data:image'):
                # Use FileHandler to convert base64 to file
                logout_selfie_file = FileHandler.save_base64_image(selfie_data, 'logout_selfie')
                form.instance.logout_selfie = logout_selfie_file
            elif not form.instance.logout_selfie:
                messages.error(self.request, "Please capture a selfie before logging out.")
                return self.form_invalid(form)
            
            # Save logout notes if provided
            logout_notes = self.request.POST.get('logout_notes', '')
            form.instance.logout_notes = logout_notes
            
            # Set logout confirmation status to pending (requires supervisor approval)
            form.instance.logout_confirmation_status = 'pending'
            # Keep overall status as pending until both are confirmed
            form.instance.confirmation_status = 'pending'
            
            response = super().form_valid(form)
            messages.success(
                self.request, 
                f"Logged out successfully! Total hours: {self.object.get_hours_rendered()}. "
                "Your logout is pending supervisor confirmation."
            )
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error processing selfie: {str(e)}")
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


class DTRResubmitView(StudentRequiredMixin, TemplateView):
    """
    View for students to resubmit a rejected DTR.
    Archives the rejected DTR to history and allows a new submission.
    
    CRUD Operation: CREATE - Creating new DTR from rejected one
    """
    
    template_name = 'student/dtr_resubmit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dtr_id = self.kwargs.get('pk')
        dtr = get_object_or_404(DTRLog, pk=dtr_id, student=self.request.user)
        
        # Only allow resubmission of rejected DTRs (check both login and logout rejection)
        is_login_rejected = dtr.login_confirmation_status == 'rejected'
        is_logout_rejected = dtr.logout_confirmation_status == 'rejected'
        
        if not is_login_rejected and not is_logout_rejected:
            messages.error(self.request, "Only rejected DTRs can be resubmitted.")
            return redirect('student:dtr_list')
        
        context['rejected_dtr'] = dtr
        context['is_login_rejected'] = is_login_rejected
        context['is_logout_rejected'] = is_logout_rejected
        
        # Determine which fields need to be resubmitted
        context['needs_login_resubmit'] = is_login_rejected
        context['needs_logout_resubmit'] = is_logout_rejected and dtr.time_out
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle resubmission of rejected DTR."""
        from .models import DTRHistory
        from datetime import datetime
        
        dtr_id = self.kwargs.get('pk')
        rejected_dtr = get_object_or_404(DTRLog, pk=dtr_id, student=request.user)
        
        # Verify it's rejected
        is_login_rejected = rejected_dtr.login_confirmation_status == 'rejected'
        is_logout_rejected = rejected_dtr.logout_confirmation_status == 'rejected'
        
        if not is_login_rejected and not is_logout_rejected:
            messages.error(request, "Only rejected DTRs can be resubmitted.")
            return redirect('student:dtr_list')
        
        try:
            # Archive the rejected DTR to history
            DTRHistory.archive_dtr(rejected_dtr, reason='resubmission')
            
            # Get form data from POST
            time_in_str = request.POST.get('time_in')
            time_out_str = request.POST.get('time_out')
            notes = request.POST.get('notes', '')
            selfie_data = request.POST.get('selfie_data', '').strip()
            logout_selfie_data = request.POST.get('logout_selfie_data', '').strip()
            
            # Parse time strings
            from datetime import time
            time_in = datetime.strptime(time_in_str, '%H:%M').time() if time_in_str else rejected_dtr.time_in
            time_out = datetime.strptime(time_out_str, '%H:%M').time() if time_out_str else rejected_dtr.time_out
            
            # Process selfie uploads
            selfie = None
            logout_selfie = None
            
            # Determine what status to use based on what was rejected
            new_login_status = 'pending'
            new_logout_status = 'pending'  # Default to pending (will be ignored if no time_out)
            
            # If login was rejected, require new login photo
            if is_login_rejected:
                if selfie_data and selfie_data.startswith('data:image'):
                    selfie = FileHandler.save_base64_image(selfie_data, 'selfie')
                else:
                    messages.error(request, "Please capture a new login photo for your resubmission.")
                    return redirect('student:dtr_resubmit', pk=rejected_dtr.pk)
            else:
                # Login was confirmed, keep the old selfie
                selfie = rejected_dtr.selfie
                new_login_status = 'confirmed'  # Keep confirmed status
            
            # Handle logout if there was a time_out
            if rejected_dtr.time_out:
                if is_logout_rejected:
                    # Logout was rejected, check for new photo
                    if logout_selfie_data and logout_selfie_data.startswith('data:image'):
                        logout_selfie = FileHandler.save_base64_image(logout_selfie_data, 'logout_selfie')
                        new_logout_status = 'pending'
                    elif rejected_dtr.logout_selfie:
                        logout_selfie = rejected_dtr.logout_selfie
                        new_logout_status = 'pending'
                    else:
                        new_logout_status = 'pending'
                else:
                    # Logout was confirmed, keep the old logout selfie
                    logout_selfie = rejected_dtr.logout_selfie
                    new_logout_status = 'confirmed'  # Keep confirmed status
            
            # Create new DTR entry with appropriate statuses
            new_dtr = DTRLog.objects.create(
                student=request.user,
                date=rejected_dtr.date,
                time_in=time_in,
                time_out=time_out if rejected_dtr.time_out else None,
                selfie=selfie,
                logout_selfie=logout_selfie,
                notes=notes,
                confirmation_status='pending',
                login_confirmation_status=new_login_status,
                logout_confirmation_status=new_logout_status,
                is_resubmission=True,
                is_valid=True
            )
            
            # Copy confirmed_by info if login was already confirmed
            if not is_login_rejected and rejected_dtr.login_confirmed_by:
                new_dtr.login_confirmed_by = rejected_dtr.login_confirmed_by
                new_dtr.login_confirmed_at = rejected_dtr.login_confirmed_at
                new_dtr.save()
            
            # Copy logout confirmed_by info if logout was already confirmed
            if rejected_dtr.time_out and not is_logout_rejected and rejected_dtr.logout_confirmed_by:
                new_dtr.logout_confirmed_by = rejected_dtr.logout_confirmed_by
                new_dtr.logout_confirmed_at = rejected_dtr.logout_confirmed_at
                new_dtr.save()
            
            # Delete the old rejected DTR
            rejected_dtr.delete()
            
            # Determine success message based on what was rejected
            if is_login_rejected and is_logout_rejected:
                msg = f"DTR for {new_dtr.date} has been resubmitted! Both login and logout are pending supervisor verification."
            elif is_login_rejected:
                msg = f"DTR for {new_dtr.date} has been resubmitted! Login is pending supervisor verification."
            else:
                msg = f"DTR for {new_dtr.date} has been resubmitted! Logout is pending supervisor verification."
            
            messages.success(request, msg)
            return redirect('student:dtr_list')
            
        except Exception as e:
            messages.error(request, f"Error resubmitting DTR: {str(e)}")
            return redirect('student:dtr_list')


class DTRHistoryView(StudentRequiredMixin, ListView):
    """
    View for students to see their DTR history (archived/rejected DTRs).
    
    CRUD Operation: READ - Reading archived DTR records
    """
    
    template_name = 'student/dtr_history.html'
    context_object_name = 'history_logs'
    paginate_by = 20
    
    def get_queryset(self):
        """Get DTR history for current student."""
        from .models import DTRHistory
        return DTRHistory.objects.filter(
            student=self.request.user
        ).order_by('-date', '-archived_at')
