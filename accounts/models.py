"""
Accounts App - User Authentication and Role Management

OOP Concept Demonstrated: CLASSES AND OBJECTS
=======================================================================
This file demonstrates OOP by defining classes that represent real-world entities.
Each model class is a blueprint for creating objects that represent users in our
OJT Management System.

Key OOP Concepts in this file:
1. Classes and Objects - User class defines the structure for user objects
2. Inheritance - User extends Django's AbstractUser
3. Encapsulation - Data (fields) and behavior (methods) are bundled together
4. Polymorphism - get_dashboard_url() returns different URLs based on role

TOPIC 2 - Classes and Objects:
-----------------------------
A CLASS is a blueprint that defines:
- Attributes (instance variables) - the data an object holds
- Methods - the behavior/actions an object can perform

An OBJECT is an instance of a class - a specific entity created from the blueprint.

Example:
    User (class) -> john_doe (object), jane_smith (object)
=======================================================================
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    OOP Concept: INHERITANCE
    -----------------------
    This class INHERITS from AbstractUser, which means:
    1. It automatically gets all fields from AbstractUser (username, email, password, etc.)
    2. It automatically gets all methods from AbstractUser (set_password, check_password, etc.)
    3. We can ADD new fields (role, profile_pic, phone, department)
    4. We can OVERRIDE methods (get_full_name, __str__, etc.)

    This is called SINGLE INHERITANCE - User has ONE parent class (AbstractUser)

    Inheritance relationship: User IS-A AbstractUser

    Real-world analogy:
    - AbstractUser is like a general "Employee" template
    - User is like a specialized "OJT System User" that inherits employee traits
      but adds specific attributes like role and profile picture

    TOPIC 3 - ENCAPSULATION:
    -----------------------
    This class demonstrates encapsulation by:
    1. Bundling data (fields) with methods that operate on that data
    2. Controlling access to data through methods (getters)
    3. The internal database storage is hidden - we interact through the Django ORM

    Instance Variables (defined as class-level field declarations in Django):
    - role: the user's role in the system
    - profile_pic: user's profile image
    - phone: contact number
    - department: department name

    Class Variables:
    - ROLES: defined at class level, shared by ALL User instances
    """

    # CLASS VARIABLE - shared by all instances of User
    # This is a tuple of tuples defining valid role choices
    # In Python OOP, class variables are defined directly in the class body
    ROLES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
    )

    # INSTANCE VARIABLES (in Django, defined as class-level field declarations)
    # Each User OBJECT will have its own value for these fields
    # These are NOT class variables - Django's metaclass magic makes them instance variables

    role = models.CharField(
        max_length=20,
        choices=ROLES,
        help_text="User's role determines their access level and dashboard"
    )

    profile_pic = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text="Optional profile picture for the user"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or course (e.g., BSIS, BSIT)"
    )

    class Meta:
        """
        Meta options for the User model.

        This inner class configures how Django handles this model.
        """
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        """
        String representation of the User object.

        OOP Concept: METHOD OVERRIDING (Polymorphism)
        -------------------------------------------
        __str__ is a SPECIAL METHOD inherited from Python's base `object` class.
        By defining it here, we OVERRIDE the default behavior to return
        a meaningful string representation.

        This is an example of POLYMORPHISM - the same method name (__str__)
        behaves differently in different classes.

        Returns:
            str: Username with role for easy identification
        """
        return f"{self.username} ({self.get_role_display()})"

    def get_full_name(self):
        """
        Return the user's full name.

        OOP Concept: ENCAPSULATION
        -------------------------
        This method ENCAPSULATES the logic for getting a user's full name.
        Instead of external code accessing first_name and last_name directly,
        they call this method, which handles the formatting.

        Benefits of encapsulation:
        1. We can change the internal logic without affecting external code
        2. We can add validation or formatting in one place
        3. The data access is controlled and consistent

        Returns:
            str: Full name or username if name is empty
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def get_role_display_label(self):
        """
        Get a formatted display label for the user's role.

        OOP Concept: ENCAPSULATION
        -------------------------
        This method controls HOW the role data is exposed/displayed.
        External code doesn't need to know about the ROLES tuple or
        how to look up the display value - this method handles it.

        Returns:
            str: Role display name with emoji indicator
        """
        role_icons = {
            'teacher': '👨‍🏫 Teacher',
            'student': '👨‍🎓 Student',
            'supervisor': '👔 Supervisor',
        }
        return role_icons.get(self.role, self.get_role_display())

    def get_dashboard_url(self):
        """
        Return the appropriate dashboard URL based on user's role.

        OOP Concept: POLYMORPHISM
        ------------------------
        This is a POLYMORPHIC method - the same method name returns different
        results depending on the OBJECT'S STATE (the role attribute).

        Same method call, different behavior based on object state:
        - teacher_user.get_dashboard_url() -> '/teacher/dashboard/'
        - student_user.get_dashboard_url() -> '/student/dashboard/'
        - supervisor_user.get_dashboard_url() -> '/supervisor/dashboard/'

        This is "behavioral polymorphism" - single interface, multiple behaviors.

        Returns:
            str: URL path to the user's role-specific dashboard
        """
        # The behavior changes based on the object's state (role)
        if self.role == 'teacher':
            return reverse('teacher:dashboard')
        elif self.role == 'student':
            return reverse('student:dashboard')
        elif self.role == 'supervisor':
            return reverse('supervisor:dashboard')
        return '/'

    def get_initials(self):
        """
        Get user's initials for avatar display.

        Returns:
            str: First letters of first and last name, or first two letters of username
        """
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()

    def is_teacher(self):
        """
        Check if user has teacher role.

        OOP Concept: PREDICATE METHOD
        ----------------------------
        Predicate methods return boolean values and typically start with
        'is_' or 'has_'. They encapsulate condition checking logic.

        Returns:
            bool: True if user is a teacher
        """
        return self.role == 'teacher'

    def is_student(self):
        """Check if user has student role."""
        return self.role == 'student'

    def is_supervisor(self):
        """Check if user has supervisor role."""
        return self.role == 'supervisor'


"""
TOPIC 1 - Introduction to OOP vs Procedural Programming:
=======================================================

PROCEDURAL APPROACH (what we DON'T do):
--------------------------------------
# Data and functions are separate
user_data = {
    'username': 'john',
    'role': 'student',
    'phone': '123-456'
}

def get_full_name(user):
    return user['first_name'] + ' ' + user['last_name']

def get_dashboard_url(user):
    if user['role'] == 'teacher':
        return '/teacher/dashboard/'
    elif user['role'] == 'student':
        return '/student/dashboard/'

# Calling procedural functions
name = get_full_name(user_data)
url = get_dashboard_url(user_data)


OBJECT-ORIENTED APPROACH (what we DO):
-------------------------------------
# Data and behavior are bundled in a class
class User:
    def __init__(self, username, role, phone):
        self.username = username  # Data
        self.role = role
        self.phone = phone

    def get_full_name(self):  # Behavior
        return f"{self.first_name} {self.last_name}"

    def get_dashboard_url(self):  # Behavior
        if self.role == 'teacher':
            return '/teacher/dashboard/'

# Creating and using objects
user = User(username='john', role='student', phone='123-456')
name = user.get_full_name()  # Method called on object
url = user.get_dashboard_url()

Benefits of OOP:
1. Organization: Related data and behavior are together
2. Reusability: Classes can be reused to create many objects
3. Maintainability: Changes to a class affect all its objects
4. Encapsulation: Internal details are hidden from external code
"""
