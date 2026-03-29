"""
Companies App - Company Records and Student Assignments

OOP Concept Demonstrated: CLASSES AND OBJECTS (TOPIC 2)
=======================================================================
This file demonstrates OOP by defining classes that represent real-world entities:
- Company: Represents an organization where students do their OJT
- Assignment: Represents the relationship between a student and a company

Key OOP Concepts:
1. Classes define the structure (attributes) and behavior (methods)
2. Each class represents a real-world entity in the OJT domain
3. ForeignKey relationships demonstrate object associations

UML Relationships (Topic 9):
---------------------------
User (1) ----supervises----> (*) Company
Company (1) <----assigned---- (*) Assignment
User (1) <----is_student---- (*) Assignment

These are ONE-TO-MANY relationships in UML notation.
=======================================================================
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Company(models.Model):
    """
    Represents a company/organization where students perform OJT.

    OOP Concept: CLASS DEFINITION
    ----------------------------
    This class defines what a Company object LOOKS like (attributes)
    and what it CAN DO (methods).

    Real-world entity: An OJT host company
    -----------------------------------------
    - name: The company's official business name
    - address: Physical location of the company
    - supervisor: The company's OJT supervisor (User with supervisor role)

    UML Association:
    ----------------
    Company *------1 User (supervisor)
    - A company HAS ONE supervisor
    - A supervisor CAN HAVE multiple companies (but typically one)

    This is a MANY-TO-ONE relationship from Company to User.
    """

    # INSTANCE VARIABLES (model fields)
    # Each Company object will have its own values for these

    name = models.CharField(
        max_length=200,
        help_text="Official company/organization name"
    )

    address = models.TextField(
        help_text="Complete physical address of the company"
    )

    # FOREIGN KEY - Relationship to User model
    # This demonstrates OBJECT ASSOCIATION in OOP
    # A Company object REFERENCES a User object (the supervisor)
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_companies',
        limit_choices_to={'role': 'supervisor'},
        help_text="Supervisor assigned to manage interns at this company"
    )

    # Optional metadata fields
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        """
        String representation of the Company.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        __str__ is inherited from Python's object class.
        We OVERRIDE it to return a meaningful representation.

        Returns:
            str: Company name
        """
        return self.name

    def get_supervisor_name(self):
        """
        Get the supervisor's name.

        OOP Concept: ENCAPSULATION
        -------------------------
        This method hides the complexity of checking if supervisor exists
        and getting their name. External code just calls this method.

        Returns:
            str: Supervisor's full name or 'No Supervisor Assigned'
        """
        if self.supervisor:
            return self.supervisor.get_full_name()
        return "No Supervisor Assigned"

    def get_intern_count(self):
        """
        Count the number of current interns at this company.

        OOP Concept: COMPUTED PROPERTY
        ----------------------------
        Instead of storing intern count (which could become stale),
        we compute it from the related assignments.

        Returns:
            int: Number of active assignments
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.assignment_set.filter(
            start_date__lte=today,
            end_date__gte=today
        ).count()


class Assignment(models.Model):
    """
    Represents a student's OJT assignment to a company.

    OOP Concept: ASSOCIATION CLASS
    -----------------------------
    In UML, this is an ASSOCIATION CLASS - it represents the relationship
    between Student (User) and Company, with additional attributes.

    Real-world entity: An OJT assignment/deployment
    -----------------------------------------------
    - A student is ASSIGNED TO a company
    - The assignment has a start date, end date, and required hours
    - This tracks the student's OJT deployment

    UML Relationship:
    ----------------
    User (student) *------* Company
              \--- Assignment ---/

    This is a MANY-TO-MANY relationship implemented via Assignment.
    One student can have multiple assignments (e.g., over different semesters).
    One company can have multiple student assignments.

    CLASS VARIABLES vs INSTANCE VARIABLES:
    -------------------------------------
    - Class variables: Defined directly in class body, shared by all instances
      Example: DEFAULT_REQUIRED_HOURS = 486

    - Instance variables: Defined as model fields, unique per instance
      Example: self.student, self.company, self.start_date
    """

    # CLASS VARIABLE - shared default value for all instances
    DEFAULT_REQUIRED_HOURS = 486

    # INSTANCE VARIABLES (model fields)
    # Each Assignment object has its own unique values for these

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignments',
        limit_choices_to={'role': 'student'},
        help_text="Student assigned to OJT"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        help_text="Company where student performs OJT"
    )

    start_date = models.DateField(
        help_text="First day of OJT"
    )

    end_date = models.DateField(
        help_text="Last day of OJT"
    )

    required_hours = models.FloatField(
        default=486,  # Using the class variable default
        help_text="Total hours required to complete OJT"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student Assignment'
        verbose_name_plural = 'Student Assignments'
        ordering = ['-start_date']
        # Ensure a student isn't assigned to the same company twice for overlapping periods
        unique_together = [['student', 'company', 'start_date']]

    def __str__(self):
        """
        String representation of the Assignment.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        Overrides the default __str__ to return a descriptive string.

        Returns:
            str: Description of the assignment
        """
        return f"{self.student.username} at {self.company.name}"

    def get_rendered_hours(self):
        """
        Calculate total hours rendered by the student for this assignment.

        OOP Concept: COMPUTED PROPERTY
        ----------------------------
        This calculates a value from related objects (DTR logs).
        It demonstrates how objects can reference each other.

        Returns:
            float: Total hours rendered
        """
        # Import here to avoid circular imports
        from dtr.models import DTRLog
        from django.db.models import Sum

        result = DTRLog.objects.filter(
            student=self.student,
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(total=Sum('hours_rendered'))

        return result['total'] or 0

    def get_progress_percentage(self):
        """
        Calculate OJT completion percentage.

        OOP Concept: DERIVED DATA
        ------------------------
        This value is DERIVED from other attributes (rendered hours / required hours).
        Instead of storing it (which could become stale), we calculate it.

        Returns:
            float: Percentage complete (0-100)
        """
        if self.required_hours <= 0:
            return 0
        rendered = self.get_rendered_hours()
        percentage = (rendered / self.required_hours) * 100
        return min(percentage, 100)  # Cap at 100%

    def is_active(self):
        """
        Check if this assignment is currently active.

        OOP Concept: PREDICATE METHOD
        ----------------------------
        Methods that return boolean and start with is_/has_ are predicates.
        They encapsulate condition logic.

        Returns:
            bool: True if today is within the assignment period
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def get_duration_days(self):
        """
        Get the total duration of the assignment in days.

        Returns:
            int: Number of days in the assignment period
        """
        return (self.end_date - self.start_date).days + 1

    def clean(self):
        """
        Validate the assignment data.

        OOP Concept: VALIDATION METHOD
        -----------------------------
        Django calls this method to validate data before saving.
        This demonstrates how classes can enforce their own constraints.

        Raises:
            ValidationError: If data is invalid
        """
        from django.core.exceptions import ValidationError
        from ojt_project.exceptions import OJTValidationError

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date.'
                })

        if self.required_hours is not None and self.required_hours <= 0:
            raise OJTValidationError(
                "Required hours must be a positive number.",
                "INVALID_REQUIRED_HOURS"
            )
