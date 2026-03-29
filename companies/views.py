"""
Companies Views - Teacher Views for Student and Assignment Management

OOP Concept Demonstrated: CLASS-BASED VIEWS AND POLYMORPHISM (TOPIC 5)
=======================================================================
This file contains teacher-specific views that demonstrate:
1. Multilevel inheritance: TeacherRequiredMixin -> BaseRoleView -> LoginRequiredMixin
2. Method overriding: Customizing get_queryset(), get_context_data(), etc.
3. Polymorphism: Same method names returning different results based on context

Each view is a CLASS that inherits from Django generic views and our mixins.
The view classes encapsulate all the logic for handling HTTP requests.

CRUD Operations (Topic 10 - Database Integration):
-----------------------------------------------
- CREATE: AssignStudentView creates new Assignment records
- READ: TeacherDashboardView, StudentDTRView read data
- UPDATE: EditAssignmentView updates Assignment records
- DELETE: DeleteAssignmentView deletes Assignment records
=======================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, Q

from accounts.mixins import TeacherRequiredMixin
from .models import Company, Assignment
from .forms import AssignmentForm
from journals.models import Journal
from dtr.models import DTRLog
from evaluations.models import Evaluation
from django.contrib.auth import get_user_model

from ojt_project.exceptions import OJTValidationError, OJTNotFoundError

User = get_user_model()


class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    """
    Teacher's main dashboard showing overview of all students.

    OOP Concept: MULTILEVEL INHERITANCE
    ----------------------------------
    This view inherits from TeacherRequiredMixin which inherits from
    BaseRoleView which inherits from LoginRequiredMixin.

    Inheritance chain:
    LoginRequiredMixin -> BaseRoleView -> TeacherRequiredMixin -> TeacherDashboardView

    Each level adds functionality:
    1. LoginRequiredMixin: Requires user to be logged in
    2. BaseRoleView: Adds role checking infrastructure
    3. TeacherRequiredMixin: Restricts to teacher role only
    4. TeacherDashboardView: Teacher-specific dashboard logic

    CRUD Operation: READ - Reading student and journal data
    """

    template_name = 'teacher/dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Prepare data for the teacher dashboard.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        We override get_context_data() from TemplateView to add
        teacher-specific context data.

        Returns:
            dict: Context data for the template
        """
        context = super().get_context_data(**kwargs)

        # Get all students with assignments
        students = User.objects.filter(role='student')

        # Prepare student data with computed fields
        student_data = []
        for student in students:
            # Get active assignment
            assignment = student.assignments.first()

            # Calculate rendered hours
            rendered_hours = DTRLog.objects.filter(
                student=student
            ).aggregate(total=Sum('hours_rendered'))['total'] or 0

            # Get required hours from assignment
            required_hours = assignment.required_hours if assignment else 486

            student_data.append({
                'student': student,
                'assignment': assignment,
                'rendered_hours': rendered_hours,
                'required_hours': required_hours,
                'progress': min((rendered_hours / required_hours) * 100, 100) if required_hours > 0 else 0
            })

        context['students'] = student_data
        context['total_students'] = len(student_data)

        # Get pending journals count
        context['pending_journals_count'] = Journal.objects.filter(
            status='pending'
        ).count()

        # Get recent journals
        context['recent_journals'] = Journal.objects.filter(
            status='pending'
        ).order_by('-submitted_at')[:5]

        return context


class AssignStudentView(TeacherRequiredMixin, CreateView):
    """
    View for teachers to assign students to companies.

    OOP Concept: CREATEVIEW INHERITANCE
    ----------------------------------
    CreateView is a generic view that handles object creation.
    We customize it for creating Assignment objects.

    CRUD Operation: CREATE - Creating new Assignment records
    """

    model = Assignment
    form_class = AssignmentForm
    template_name = 'teacher/assign_student.html'
    success_url = reverse_lazy('teacher:dashboard')

    def form_valid(self, form):
        """
        Handle successful assignment creation.

        Exception Handling: We wrap in try-except to catch validation errors.
        """
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                f"Successfully assigned {form.instance.student.get_full_name()} "
                f"to {form.instance.company.name}"
            )
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class EditAssignmentView(TeacherRequiredMixin, UpdateView):
    """
    View for editing existing assignments.

    OOP Concept: UPDATEVIEW INHERITANCE
    ----------------------------------
    UpdateView handles object updates with form handling.

    CRUD Operation: UPDATE - Updating Assignment records
    """

    model = Assignment
    form_class = AssignmentForm
    template_name = 'teacher/edit_assignment.html'
    success_url = reverse_lazy('teacher:dashboard')

    def form_valid(self, form):
        """Handle successful assignment update."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Assignment updated successfully.")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class DeleteAssignmentView(TeacherRequiredMixin, DeleteView):
    """
    View for deleting assignments.

    OOP Concept: DELETEVIEW INHERITANCE
    ----------------------------------
    DeleteView handles object deletion with confirmation.

    CRUD Operation: DELETE - Deleting Assignment records
    """

    model = Assignment
    template_name = 'teacher/delete_assignment.html'
    success_url = reverse_lazy('teacher:dashboard')

    def delete(self, request, *args, **kwargs):
        """Handle assignment deletion with success message."""
        assignment = self.get_object()
        messages.success(
            request,
            f"Assignment for {assignment.student.get_full_name()} has been removed."
        )
        return super().delete(request, *args, **kwargs)


class StudentDTRView(TeacherRequiredMixin, ListView):
    """
    View for teachers to see a student's DTR logs.

    OOP Concept: LISTVIEW WITH FILTERED QUERYSET
    -------------------------------------------
    We override get_queryset() to filter DTR logs for a specific student.
    This demonstrates how the same ListView class can show different data
    based on URL parameters.

    CRUD Operation: READ - Reading DTRLog records
    """

    model = DTRLog
    template_name = 'teacher/student_dtr.html'
    context_object_name = 'dtr_logs'
    paginate_by = 20

    def get_queryset(self):
        """
        Get DTR logs for the specified student.

        OOP Concept: METHOD OVERRIDING FOR FILTERING
        -------------------------------------------
        We override get_queryset() to filter by student ID from URL.

        Returns:
            QuerySet: DTR logs for the specific student
        """
        student_id = self.kwargs.get('student_id')
        return DTRLog.objects.filter(
            student_id=student_id
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        """Add student info to context."""
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_id')

        try:
            context['student'] = User.objects.get(pk=student_id, role='student')
        except User.DoesNotExist:
            raise OJTNotFoundError(
                f"Student with ID {student_id} not found",
                "STUDENT_NOT_FOUND"
            )

        # Calculate total hours
        context['total_hours'] = self.get_queryset().aggregate(
            total=Sum('hours_rendered')
        )['total'] or 0

        return context


class JournalListView(TeacherRequiredMixin, ListView):
    """
    View for teachers to see all student journals.

    OOP Concept: LISTVIEW WITH FILTERING
    -----------------------------------
    We support filtering by status using URL query parameters.

    CRUD Operation: READ - Reading Journal records
    """

    model = Journal
    template_name = 'teacher/journal_list.html'
    context_object_name = 'journals'
    paginate_by = 20

    def get_queryset(self):
        """
        Get journals with optional status filter.

        OOP Concept: DYNAMIC FILTERING
        -----------------------------
        The queryset changes based on request parameters.
        """
        queryset = Journal.objects.all().order_by('-submitted_at')

        status_filter = self.request.GET.get('status')
        if status_filter in ['pending', 'approved', 'rejected']:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Add filter status to context."""
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'all')
        context['pending_count'] = Journal.objects.filter(status='pending').count()
        return context


class JournalReviewView(TeacherRequiredMixin, UpdateView):
    """
    View for reviewing and approving/rejecting journals.

    OOP Concept: CUSTOM FORM HANDLING
    --------------------------------
    We handle form submission differently based on which button was clicked.

    CRUD Operation: UPDATE - Updating Journal status and feedback
    """

    model = Journal
    fields = ['feedback']
    template_name = 'teacher/journal_review.html'
    success_url = reverse_lazy('teacher:journals')

    def post(self, request, *args, **kwargs):
        """
        Handle journal approval or rejection.

        OOP Concept: METHOD OVERRIDING FOR CUSTOM BEHAVIOR
        -------------------------------------------------
        We override post() to check which action was requested.
        """
        self.object = self.get_object()
        feedback = request.POST.get('feedback', '')

        if 'approve' in request.POST:
            self.object.status = 'approved'
            self.object.feedback = feedback
            self.object.save()
            messages.success(request, "Journal has been approved.")

        elif 'reject' in request.POST:
            if not feedback:
                messages.error(request, "Please provide feedback when rejecting a journal.")
                return self.get(request, *args, **kwargs)
            self.object.status = 'rejected'
            self.object.feedback = feedback
            self.object.save()
            messages.warning(request, "Journal has been rejected.")

        return redirect(self.success_url)


class EvaluationListView(TeacherRequiredMixin, ListView):
    """
    View for teachers to see all supervisor evaluations.

    CRUD Operation: READ - Reading Evaluation records
    """

    model = Evaluation
    template_name = 'teacher/evaluation_list.html'
    context_object_name = 'evaluations'
    paginate_by = 20

    def get_queryset(self):
        """Get all evaluations ordered by date."""
        return Evaluation.objects.all().order_by('-created_at')


# ==================== COMPANY MANAGEMENT VIEWS ====================

class CompanyListView(TeacherRequiredMixin, ListView):
    """
    View for teachers to see all companies.

    CRUD Operation: READ - Reading Company records
    """

    model = Company
    template_name = 'teacher/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20

    def get_queryset(self):
        """Get all companies ordered by name."""
        return Company.objects.all().order_by('name')


class CompanyCreateView(TeacherRequiredMixin, CreateView):
    """
    View for teachers to add new companies.

    CRUD Operation: CREATE - Creating new Company records
    """

    model = Company
    template_name = 'teacher/company_form.html'
    fields = ['name', 'address', 'supervisor', 'contact_email', 'contact_phone']
    success_url = reverse_lazy('teacher:companies')

    def get_form(self, form_class=None):
        """Customize form with Bootstrap classes and filter supervisor choices."""
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'address':
                field.widget.attrs['rows'] = 3
        # Limit supervisor choices to users with supervisor role
        form.fields['supervisor'].queryset = User.objects.filter(role='supervisor')
        return form

    def form_valid(self, form):
        """Handle successful company creation."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Company '{form.instance.name}' has been added successfully."
        )
        return response


class CompanyUpdateView(TeacherRequiredMixin, UpdateView):
    """
    View for teachers to edit existing companies.

    CRUD Operation: UPDATE - Updating Company records
    """

    model = Company
    template_name = 'teacher/company_form.html'
    fields = ['name', 'address', 'supervisor', 'contact_email', 'contact_phone']
    success_url = reverse_lazy('teacher:companies')

    def get_form(self, form_class=None):
        """Customize form with Bootstrap classes and filter supervisor choices."""
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'address':
                field.widget.attrs['rows'] = 3
        form.fields['supervisor'].queryset = User.objects.filter(role='supervisor')
        return form

    def form_valid(self, form):
        """Handle successful company update."""
        response = super().form_valid(form)
        messages.success(self.request, "Company updated successfully.")
        return response


class CompanyDeleteView(TeacherRequiredMixin, DeleteView):
    """
    View for teachers to delete companies.

    CRUD Operation: DELETE - Deleting Company records
    """

    model = Company
    template_name = 'teacher/company_confirm_delete.html'
    success_url = reverse_lazy('teacher:companies')

    def delete(self, request, *args, **kwargs):
        """Handle company deletion with success message."""
        company = self.get_object()
        messages.success(request, f"Company '{company.name}' has been deleted.")
        return super().delete(request, *args, **kwargs)


# ==================== STUDENT MANAGEMENT VIEWS ====================

class StudentListView(TeacherRequiredMixin, ListView):
    """
    View for teachers to see all students.

    CRUD Operation: READ - Reading Student records
    """

    model = User
    template_name = 'teacher/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        """Get all students ordered by name."""
        return User.objects.filter(role='student').order_by('last_name', 'first_name')


class StudentCreateView(TeacherRequiredMixin, CreateView):
    """
    View for teachers to add new students.

    CRUD Operation: CREATE - Creating new Student records
    """

    model = User
    template_name = 'teacher/student_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'department']
    success_url = reverse_lazy('teacher:students')

    def get_form(self, form_class=None):
        """Customize form with Bootstrap classes."""
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
        return form

    def form_valid(self, form):
        """Handle successful student creation."""
        # Set role to student
        form.instance.role = 'student'
        # Set a default password (student should change it)
        user = form.save(commit=False)
        user.set_password('student123')  # Default password
        user.save()
        messages.success(
            self.request,
            f"Student '{user.get_full_name()}' has been added. Default password is 'student123'."
        )
        return redirect(self.success_url)


class StudentUpdateView(TeacherRequiredMixin, UpdateView):
    """
    View for teachers to edit existing students.

    CRUD Operation: UPDATE - Updating Student records
    """

    model = User
    template_name = 'teacher/student_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'department']
    success_url = reverse_lazy('teacher:students')

    def get_queryset(self):
        """Only allow editing students."""
        return User.objects.filter(role='student')

    def get_form(self, form_class=None):
        """Customize form with Bootstrap classes."""
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
        return form

    def form_valid(self, form):
        """Handle successful student update."""
        response = super().form_valid(form)
        messages.success(self.request, "Student updated successfully.")
        return response


class StudentDeleteView(TeacherRequiredMixin, DeleteView):
    """
    View for teachers to delete students.

    CRUD Operation: DELETE - Deleting Student records
    """

    model = User
    template_name = 'teacher/student_confirm_delete.html'
    success_url = reverse_lazy('teacher:students')

    def get_queryset(self):
        """Only allow deleting students."""
        return User.objects.filter(role='student')

    def delete(self, request, *args, **kwargs):
        """Handle student deletion with success message."""
        student = self.get_object()
        messages.success(request, f"Student '{student.get_full_name()}' has been deleted.")
        return super().delete(request, *args, **kwargs)


class StudentResetPasswordView(TeacherRequiredMixin, DetailView):
    """
    View for teachers to reset a student's password.
    """

    model = User
    template_name = 'teacher/student_reset_password.html'

    def get_queryset(self):
        """Only allow resetting student passwords."""
        return User.objects.filter(role='student')

    def post(self, request, *args, **kwargs):
        """Reset the student's password to default."""
        student = self.get_object()
        student.set_password('student123')
        student.save()
        messages.success(
            request,
            f"Password for '{student.get_full_name()}' has been reset to 'student123'."
        )
        return redirect('teacher:students')
