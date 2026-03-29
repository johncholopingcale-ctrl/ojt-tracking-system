"""
Accounts Views - Authentication and User Management Views

OOP Concept Demonstrated: CLASS-BASED VIEWS AND INHERITANCE (TOPIC 4 & 5)
=======================================================================
Django class-based views demonstrate key OOP principles:
1. Inheritance: Views inherit from Django's generic views
2. Polymorphism: Methods like get_context_data() are overridden
3. Encapsulation: View logic is encapsulated in class methods

View inheritance hierarchy:
    View (base Django view)
        |
    TemplateView (adds template rendering)
        |
    FormView (adds form handling)
        |
    CreateView (adds object creation)
=======================================================================
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User
from .mixins import StudentRequiredMixin, TeacherRequiredMixin, SupervisorRequiredMixin

from ojt_project.exceptions import OJTValidationError


class CustomLoginView(LoginView):
    """
    Custom login view with role-based redirect.

    OOP Concept: INHERITANCE AND METHOD OVERRIDING
    ---------------------------------------------
    This class INHERITS from Django's LoginView and OVERRIDES
    specific methods to customize behavior.

    Overridden methods:
    - form_valid(): Custom post-login handling
    - get_success_url(): Role-based redirect URL

    POLYMORPHISM: The same method name (get_success_url) returns
    different URLs based on the user's role.
    """

    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Handle successful login.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        We override form_valid() to add a welcome message.
        The super().form_valid(form) call ensures parent behavior runs.

        This demonstrates the TEMPLATE METHOD pattern:
        - Parent defines the overall flow
        - Child overrides specific steps
        """
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Welcome back, {self.request.user.get_full_name()}!"
        )
        return response

    def get_success_url(self):
        """
        Return URL based on user's role after login.

        OOP Concept: POLYMORPHIC REDIRECT
        --------------------------------
        This method returns different URLs based on user's role.
        Same method, different behavior - that's polymorphism!

        Returns:
            str: URL to redirect to after login
        """
        user = self.request.user
        return user.get_dashboard_url()


class CustomLogoutView(LogoutView):
    """
    Custom logout view with message.

    OOP Concept: SIMPLE INHERITANCE
    ------------------------------
    This class inherits from LogoutView with minimal customization.
    Sometimes inheritance is just for configuration.
    """

    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        """Add logout message."""
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """
    User registration view.

    OOP Concept: CREATEVIEW INHERITANCE
    ----------------------------------
    CreateView is a GENERIC VIEW that handles:
    - Displaying a form (GET)
    - Processing form submission (POST)
    - Creating a new model instance
    - Redirecting after success

    We customize it by:
    - Specifying the model and form class
    - Overriding form_valid() for auto-login
    - Using our custom template
    """

    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        """
        Handle valid form submission.

        OOP Concept: EXTENDING PARENT BEHAVIOR
        -------------------------------------
        We call super().form_valid(form) to get parent behavior,
        then ADD our own logic (success message and redirect to login).

        This is EXTENSION not replacement:
        1. Parent creates the user object
        2. We add a welcome message and redirect to login

        Returns:
            HttpResponse: Redirect to login page
        """
        # Let parent create the user
        response = super().form_valid(form)

        # Get the created user for the message
        user = form.instance

        messages.success(
            self.request,
            f"Account created successfully! Welcome {user.get_full_name()}. "
            f"Please log in to continue."
        )

        # Redirect to login page
        return redirect('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to their dashboard."""
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        return super().dispatch(request, *args, **kwargs)


class BaseProfileUpdateView(UpdateView):
    """
    Base profile update view for all user roles.

    OOP Concept: ABSTRACT BASE CLASS
    -------------------------------
    This serves as the base class for role-specific profile views.
    It contains all common profile update logic that is shared
    across all roles (student, teacher, supervisor).

    Subclasses only need to specify:
    - The appropriate mixin for role checking
    - The template to use
    - The success URL

    This follows the DRY (Don't Repeat Yourself) principle.
    """

    model = User
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        """
        Return the current user as the object to update.

        OOP Concept: METHOD OVERRIDING FOR CUSTOMIZATION
        -----------------------------------------------
        By default, UpdateView expects a pk or slug in the URL.
        We override get_object() to always return the current user.

        Returns:
            User: The currently logged-in user
        """
        return self.request.user

    def form_valid(self, form):
        """
        Handle successful profile update.

        Exception Handling: We wrap the save in try-except
        to handle potential file upload errors.
        """
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Profile updated successfully!")
            return response
        except OJTValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Add extra context for the profile template.

        OOP Concept: EXTENDING TEMPLATE CONTEXT
        --------------------------------------
        We call super().get_context_data() to get parent's context,
        then add our own data to it.

        Returns:
            dict: Template context dictionary
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Profile'
        return context


class ProfileUpdateView(StudentRequiredMixin, BaseProfileUpdateView):
    """
    Student profile update view.

    OOP Concept: MULTIPLE INHERITANCE (Mixin)
    ----------------------------------------
    This view inherits from BOTH:
    - StudentRequiredMixin (for role checking)
    - BaseProfileUpdateView (for profile update functionality)

    This is MULTIPLE INHERITANCE - combining functionality from
    multiple parent classes.
    """

    template_name = 'student/profile.html'
    success_url = reverse_lazy('student:profile')


class TeacherProfileUpdateView(TeacherRequiredMixin, BaseProfileUpdateView):
    """
    Teacher profile update view.

    OOP Concept: INHERITANCE REUSE
    -----------------------------
    By inheriting from BaseProfileUpdateView, this class reuses
    all profile update logic and only needs to specify:
    - TeacherRequiredMixin for role checking
    - Teacher-specific template
    - Teacher-specific success URL
    """

    template_name = 'teacher/profile.html'
    success_url = reverse_lazy('teacher:profile')


class SupervisorProfileUpdateView(SupervisorRequiredMixin, BaseProfileUpdateView):
    """
    Supervisor profile update view.

    OOP Concept: INHERITANCE REUSE
    -----------------------------
    By inheriting from BaseProfileUpdateView, this class reuses
    all profile update logic and only needs to specify:
    - SupervisorRequiredMixin for role checking
    - Supervisor-specific template
    - Supervisor-specific success URL
    """

    template_name = 'supervisor/profile.html'
    success_url = reverse_lazy('supervisor:profile')
