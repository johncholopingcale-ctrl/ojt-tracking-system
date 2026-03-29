"""
Journals App - Weekly Journal Submission and Review

OOP Concept Demonstrated: ABSTRACTION (TOPIC 6)
=======================================================================
This file demonstrates ABSTRACTION through the OJTBaseModel inheritance.
The Journal class inherits from OJTBaseModel and implements the abstract
method get_display_info().

Key OOP Concepts:
1. Abstraction: Journal inherits from abstract base class OJTBaseModel
2. Implementation: Journal MUST implement get_display_info()
3. Encapsulation: Status logic is encapsulated in methods

Abstract class relationship:
OJTBaseModel (abstract) --> Journal (concrete)

The abstract class defines WHAT should be done (get_display_info),
the concrete class defines HOW it's done.
=======================================================================
"""

from django.db import models
from django.contrib.auth import get_user_model

from ojt_project.base_models import OJTBaseModel
from ojt_project.exceptions import OJTValidationError

User = get_user_model()


class Journal(OJTBaseModel):
    """
    Weekly OJT journal submission.

    OOP Concept: INHERITANCE FROM ABSTRACT CLASS (TOPIC 6)
    -----------------------------------------------------
    This class INHERITS from OJTBaseModel, an ABSTRACT class.
    Because OJTBaseModel is abstract:
    1. It cannot be instantiated directly
    2. Its abstract methods MUST be implemented by subclasses
    3. Its concrete methods and fields are inherited

    What Journal inherits from OJTBaseModel:
    - created_at field (inherited)
    - updated_at field (inherited)
    - get_created_date_formatted() method (inherited)
    - get_updated_at_formatted() method (inherited)

    What Journal MUST implement:
    - get_display_info() - abstract method that returns display string

    Real-world entity: A weekly journal entry
    -----------------------------------------
    - student: Who wrote the journal
    - week_number: Which week of OJT
    - content: The journal text
    - status: pending/approved/rejected
    - feedback: Teacher's feedback
    """

    # CLASS VARIABLES - status choices
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    # INSTANCE VARIABLES (model fields)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='journals',
        limit_choices_to={'role': 'student'},
        help_text="Student who submitted this journal"
    )

    week_number = models.IntegerField(
        help_text="Week number of OJT (1, 2, 3, etc.)"
    )

    content = models.TextField(
        help_text="Journal content/reflection"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Review status"
    )

    feedback = models.TextField(
        blank=True,
        help_text="Teacher's feedback on the journal"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the journal was submitted"
    )

    # Note: updated_at is inherited from OJTBaseModel!

    class Meta:
        verbose_name = 'Journal'
        verbose_name_plural = 'Journals'
        ordering = ['-submitted_at']
        # One journal per week per student
        unique_together = [['student', 'week_number']]

    def __str__(self):
        """String representation of the journal."""
        return f"Week {self.week_number} - {self.student.username}"

    def get_display_info(self):
        """
        Implementation of abstract method from OJTBaseModel.

        OOP Concept: IMPLEMENTING ABSTRACT METHOD
        ----------------------------------------
        This method is REQUIRED by the abstract base class.
        If we don't implement it, Python would raise an error.

        The abstract class defines the CONTRACT:
        - All OJTBaseModel subclasses must have get_display_info()
        - It must return a string describing the object

        Each subclass implements it DIFFERENTLY:
        - Journal returns week number and status
        - Evaluation (in another file) returns rating and recommendation

        This is ABSTRACTION: the base class says WHAT to do,
        the subclass decides HOW to do it.

        Returns:
            str: Human-readable display information
        """
        return f"Journal Week {self.week_number}: {self.get_status_display()}"

    def get_status_badge_class(self):
        """
        Get Bootstrap badge class for status display.

        OOP Concept: ENCAPSULATION
        -------------------------
        This method hides the mapping logic between status and CSS class.
        Templates just call this method without knowing the mapping.

        Returns:
            str: Bootstrap badge class
        """
        status_classes = {
            'pending': 'badge-warning',
            'approved': 'badge-success',
            'rejected': 'badge-danger',
        }
        return status_classes.get(self.status, 'badge-secondary')

    def can_edit(self):
        """
        Check if this journal can be edited.

        OOP Concept: BUSINESS LOGIC ENCAPSULATION
        ----------------------------------------
        The rule "only pending journals can be edited" is encapsulated here.
        Views don't need to know the rule - they just call can_edit().

        Returns:
            bool: True if journal can be edited
        """
        return self.status == 'pending'

    def can_delete(self):
        """
        Check if this journal can be deleted.

        Returns:
            bool: True if journal can be deleted
        """
        return self.status == 'pending'

    def approve(self, feedback=''):
        """
        Approve this journal.

        OOP Concept: STATE TRANSITION METHOD
        -----------------------------------
        Instead of directly changing status, we use methods that
        encapsulate the state transition logic.

        Args:
            feedback: Optional feedback text
        """
        self.status = 'approved'
        if feedback:
            self.feedback = feedback
        self.save()

    def reject(self, feedback):
        """
        Reject this journal with required feedback.

        OOP Concept: VALIDATION IN METHODS
        ---------------------------------
        The method enforces that feedback is required for rejection.

        Args:
            feedback: Required feedback explaining the rejection

        Raises:
            OJTValidationError: If feedback is empty
        """
        if not feedback:
            raise OJTValidationError(
                "Feedback is required when rejecting a journal.",
                "FEEDBACK_REQUIRED"
            )
        self.status = 'rejected'
        self.feedback = feedback
        self.save()

    def clean(self):
        """
        Validate journal data.

        Raises:
            ValidationError: If validation fails
        """
        from django.core.exceptions import ValidationError

        if self.week_number is not None and self.week_number < 1:
            raise ValidationError({
                'week_number': 'Week number must be at least 1.'
            })

        if not self.content or len(self.content.strip()) < 50:
            raise ValidationError({
                'content': 'Journal content must be at least 50 characters.'
            })
