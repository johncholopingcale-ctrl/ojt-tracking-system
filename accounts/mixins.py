"""
Accounts Mixins - Role-Based Access Control

OOP Concept Demonstrated: INHERITANCE AND MIXINS (TOPIC 4)
=======================================================================
This file demonstrates INHERITANCE through mixin classes that provide
reusable functionality for Django class-based views.

INHERITANCE HIERARCHY:
---------------------
    LoginRequiredMixin (Django built-in)
           |
    BaseRoleView (our custom base)
        /    |    \
TeacherRequired  StudentRequired  SupervisorRequired

This is MULTILEVEL INHERITANCE:
- BaseRoleView inherits from LoginRequiredMixin
- TeacherRequiredMixin inherits from BaseRoleView
- View classes inherit from TeacherRequiredMixin + other Django views

What is a Mixin?
---------------
A mixin is a class that provides methods and attributes to other classes
through multiple inheritance. Mixins are designed to be "mixed in" with
other classes to add functionality.

Key characteristics of mixins:
1. They don't work standalone - they need to be combined with other classes
2. They provide a specific piece of functionality
3. They allow code reuse without deep inheritance hierarchies
4. Python supports multiple inheritance, making mixins powerful

SOLID Principle - Open/Closed:
This mixin system is OPEN for extension (create new role mixins)
but CLOSED for modification (existing mixins don't need changes).
=======================================================================
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


class BaseRoleView(LoginRequiredMixin):
    """
    Base class for all role-protected views.

    OOP Concept: BASE CLASS / PARENT CLASS
    -------------------------------------
    This class serves as the base (parent) for all role-specific mixins.
    It provides common functionality that all role-protected views need.

    Inheritance demonstrated:
    - BaseRoleView IS-A LoginRequiredMixin (single inheritance)
    - TeacherRequiredMixin IS-A BaseRoleView (multilevel inheritance)

    This class adds to LoginRequiredMixin:
    1. Role checking (allowed_roles attribute)
    2. Custom redirect behavior based on user role
    3. Permission denied handling

    Usage:
        class MyView(TeacherRequiredMixin, TemplateView):
            template_name = 'my_template.html'
    """

    # Class attribute - can be overridden by subclasses
    allowed_roles = []
    redirect_authenticated = True

    def dispatch(self, request, *args, **kwargs):
        """
        Handle the request dispatch with role checking.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        We OVERRIDE the dispatch method from LoginRequiredMixin.
        This method is called before get() or post() to handle
        preliminary checks like authentication and permissions.

        The super().dispatch() call invokes the PARENT'S dispatch method,
        demonstrating the use of super() in inheritance.

        Args:
            request: HTTP request object
            *args, **kwargs: Additional arguments

        Returns:
            HttpResponse: Either the view response or a redirect
        """
        # First, check if user is authenticated (parent class behavior)
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        # Then, check role permissions
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            messages.warning(
                request,
                f"Access denied. This page is for {', '.join(self.allowed_roles)} only."
            )
            # Redirect to user's own dashboard
            return redirect(request.user.get_dashboard_url())

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add common context data for all role-protected views.

        OOP Concept: PROVIDING COMMON FUNCTIONALITY
        ------------------------------------------
        This method adds data that ALL role-protected views need,
        reducing code duplication in subclasses.

        Subclasses can EXTEND this by calling super().get_context_data(**kwargs)
        and then adding their own context data.

        Returns:
            dict: Context dictionary with user role info
        """
        context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else {}
        context['current_user_role'] = getattr(self.request.user, 'role', None)
        return context


class TeacherRequiredMixin(BaseRoleView):
    """
    Mixin that requires the user to have the 'teacher' role.

    OOP Concept: INHERITANCE SPECIALIZATION
    --------------------------------------
    This class INHERITS from BaseRoleView and SPECIALIZES it
    for teacher access only by setting allowed_roles.

    INHERITANCE CHAIN:
    LoginRequiredMixin -> BaseRoleView -> TeacherRequiredMixin

    This is MULTILEVEL INHERITANCE - each class builds on the previous:
    1. LoginRequiredMixin: Requires authentication
    2. BaseRoleView: Adds role checking capability
    3. TeacherRequiredMixin: Specifies 'teacher' as allowed role

    SOLID Principle - Liskov Substitution:
    Any view that works with BaseRoleView should work with TeacherRequiredMixin,
    because TeacherRequiredMixin IS-A BaseRoleView with additional constraints.

    Usage:
        class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
            template_name = 'teacher/dashboard.html'

            # This view inherits:
            # - Login requirement (from LoginRequiredMixin)
            # - Role checking (from BaseRoleView)
            # - Teacher role restriction (from TeacherRequiredMixin)
    """

    allowed_roles = ['teacher']


class StudentRequiredMixin(BaseRoleView):
    """
    Mixin that requires the user to have the 'student' role.

    OOP Concept: SIBLING CLASSES
    ---------------------------
    StudentRequiredMixin and TeacherRequiredMixin are "siblings" -
    they share the same parent (BaseRoleView) but specialize differently.

    This demonstrates POLYMORPHISM at the class level:
    - Both mixins work the same way (enforce allowed_roles)
    - But each enforces a DIFFERENT role

    Usage:
        class StudentDashboardView(StudentRequiredMixin, TemplateView):
            template_name = 'student/dashboard.html'
    """

    allowed_roles = ['student']


class SupervisorRequiredMixin(BaseRoleView):
    """
    Mixin that requires the user to have the 'supervisor' role.

    OOP Concept: COMPLETE INHERITANCE EXAMPLE
    ----------------------------------------
    This class demonstrates all inheritance concepts:

    1. It INHERITS from BaseRoleView
    2. It SPECIALIZES the allowed_roles class attribute
    3. It can be MIXED IN with other classes (multiple inheritance)
    4. Views that use it SUBSTITUTE for BaseRoleView (LSP)

    Usage:
        class SupervisorDashboardView(SupervisorRequiredMixin, TemplateView):
            template_name = 'supervisor/dashboard.html'
    """

    allowed_roles = ['supervisor']


def role_required(allowed_roles):
    """
    Decorator for function-based views that requires specific roles.

    OOP Concept: DECORATOR PATTERN
    -----------------------------
    This is a FUNCTION DECORATOR that wraps view functions to add
    role checking. While not a class, decorators are an important
    OOP design pattern.

    The decorator pattern allows adding behavior to functions/objects
    without modifying their code - following Open/Closed Principle.

    How decorators work:
    1. The decorator receives the function to wrap
    2. It returns a NEW function that adds behavior
    3. The original function is called from within the wrapper

    Args:
        allowed_roles (list): List of roles allowed to access the view

    Returns:
        function: Decorator function that wraps the view

    Usage (function-based views):
        @role_required(['teacher'])
        def teacher_dashboard(request):
            return render(request, 'teacher/dashboard.html')

        @role_required(['student'])
        def student_dashboard(request):
            return render(request, 'student/dashboard.html')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check authentication
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')

            # Check role
            if request.user.role not in allowed_roles:
                messages.warning(
                    request,
                    f"Access denied. This page is for {', '.join(allowed_roles)} only."
                )
                return redirect(request.user.get_dashboard_url())

            # Call the original view function
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


"""
INHERITANCE SUMMARY (Topic 4):
=============================

SINGLE INHERITANCE:
------------------
class Child(Parent):
    pass
# Child inherits ALL attributes and methods from Parent

MULTILEVEL INHERITANCE:
----------------------
class GrandParent:
    pass

class Parent(GrandParent):
    pass

class Child(Parent):
    pass
# Child inherits from Parent, which inherits from GrandParent

MULTIPLE INHERITANCE (Mixins):
-----------------------------
class Mixin1:
    def method1(self):
        pass

class Mixin2:
    def method2(self):
        pass

class MyClass(Mixin1, Mixin2, BaseClass):
    pass
# MyClass has methods from Mixin1, Mixin2, AND BaseClass

METHOD RESOLUTION ORDER (MRO):
-----------------------------
Python uses C3 Linearization to determine which method to call
when multiple parent classes have the same method name.

To see the MRO:
    print(MyClass.__mro__)
    # or
    print(MyClass.mro())
"""
