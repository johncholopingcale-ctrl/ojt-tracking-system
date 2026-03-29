"""
Journals Views - Student Journal Management

OOP Concept: VIEWS WITH BUSINESS LOGIC ENFORCEMENT
=================================================
These views demonstrate how to enforce business rules:
- Only pending journals can be edited or deleted
- Exception handling for validation errors
"""

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from accounts.mixins import StudentRequiredMixin
from .models import Journal
from .forms import JournalForm

from ojt_project.exceptions import OJTValidationError


class JournalCreateView(StudentRequiredMixin, CreateView):
    """
    Create a new journal entry.

    CRUD Operation: CREATE
    """

    model = Journal
    form_class = JournalForm
    template_name = 'student/journal_submit.html'
    success_url = reverse_lazy('student:journal_list')

    def form_valid(self, form):
        """
        Handle journal submission.

        Exception Handling: Wrapped in try-except
        """
        try:
            form.instance.student = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, "Journal submitted successfully!")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class JournalEditView(StudentRequiredMixin, UpdateView):
    """
    Edit a pending journal.

    OOP Concept: BUSINESS RULE ENFORCEMENT
    -------------------------------------
    Only pending journals can be edited.
    """

    model = Journal
    form_class = JournalForm
    template_name = 'student/journal_edit.html'
    success_url = reverse_lazy('student:journal_list')

    def get_queryset(self):
        """Limit to current student's pending journals."""
        return Journal.objects.filter(
            student=self.request.user,
            status='pending'
        )

    def dispatch(self, request, *args, **kwargs):
        """
        Check if journal can be edited before allowing access.

        OOP Concept: PRE-CONDITION CHECK
        -------------------------------
        We check the business rule before processing the request.
        """
        obj = self.get_object()
        if not obj.can_edit():
            messages.error(
                request,
                "You can only edit pending journals. This journal has been reviewed."
            )
            return redirect('student:journal_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle journal edit."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Journal updated successfully!")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class JournalDeleteView(StudentRequiredMixin, DeleteView):
    """
    Delete a pending journal.

    OOP Concept: BUSINESS RULE ENFORCEMENT
    -------------------------------------
    Only pending journals can be deleted.
    """

    model = Journal
    template_name = 'student/journal_delete.html'
    success_url = reverse_lazy('student:journal_list')

    def get_queryset(self):
        """Limit to current student's pending journals."""
        return Journal.objects.filter(
            student=self.request.user,
            status='pending'
        )

    def dispatch(self, request, *args, **kwargs):
        """Check if journal can be deleted."""
        obj = self.get_object()
        if not obj.can_delete():
            messages.error(
                request,
                "You can only delete pending journals. This journal has been reviewed."
            )
            return redirect('student:journal_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete with success message."""
        messages.success(request, "Journal deleted successfully.")
        return super().delete(request, *args, **kwargs)
