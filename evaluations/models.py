"""
Evaluations App - Supervisor Performance Evaluations

OOP Concept Demonstrated: ABSTRACTION (TOPIC 6)
=======================================================================
This file demonstrates ABSTRACTION through inheritance from OJTBaseModel.
The Evaluation class, like Journal, inherits from the abstract OJTBaseModel
and implements the required get_display_info() method.

This demonstrates:
1. Multiple concrete classes from same abstract base
2. Each implementation with different behavior
3. Polymorphism: same method, different implementations
=======================================================================
"""

from django.db import models
from django.contrib.auth import get_user_model

from ojt_project.base_models import OJTBaseModel

User = get_user_model()


class Evaluation(OJTBaseModel):
    """
    Supervisor's evaluation of a student's OJT performance.

    OOP Concept: INHERITANCE FROM ABSTRACT CLASS (TOPIC 6)
    -----------------------------------------------------
    This class INHERITS from OJTBaseModel, the same abstract base
    that Journal inherits from. This demonstrates:

    1. One abstract class, multiple concrete implementations
    2. Each concrete class implements the abstract method differently
    3. Polymorphism: same interface, different behavior

    Inherited from OJTBaseModel:
    - created_at field
    - updated_at field
    - get_created_date_formatted() method
    - get_updated_at_formatted() method

    Must implement:
    - get_display_info() method

    Real-world entity: A performance evaluation
    ------------------------------------------
    - supervisor: Who gave the evaluation
    - student: Who was evaluated
    - work_quality: Rating 1-5
    - attitude: Rating 1-5
    - overall_rating: Rating 1-5
    - recommendation: Final recommendation
    - notes: Additional comments
    """

    # CLASS VARIABLES - recommendation choices
    RECOMMENDATION_CHOICES = (
        ('recommended', 'Recommended'),
        ('not_recommended', 'Not Recommended'),
        ('highly_recommended', 'Highly Recommended'),
    )

    # RATING CHOICES for 1-5 star ratings
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )

    # INSTANCE VARIABLES (model fields)
    supervisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_evaluations',
        limit_choices_to={'role': 'supervisor'},
        help_text="Supervisor who gave this evaluation"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_evaluations',
        limit_choices_to={'role': 'student'},
        help_text="Student being evaluated"
    )

    work_quality = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Quality of work produced (1-5)"
    )

    attitude = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Professional attitude and behavior (1-5)"
    )

    overall_rating = models.FloatField(
        help_text="Overall performance rating (1-5)"
    )

    recommendation = models.CharField(
        max_length=30,
        choices=RECOMMENDATION_CHOICES,
        help_text="Final recommendation"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional comments and observations"
    )

    # Note: created_at and updated_at are inherited from OJTBaseModel!

    class Meta:
        verbose_name = 'Evaluation'
        verbose_name_plural = 'Evaluations'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the evaluation."""
        return f"Evaluation: {self.student.username} by {self.supervisor.username}"

    def get_display_info(self):
        """
        Implementation of abstract method from OJTBaseModel.

        OOP Concept: POLYMORPHISM IN ABSTRACT METHOD IMPLEMENTATION
        ----------------------------------------------------------
        Both Journal and Evaluation implement get_display_info(),
        but they return DIFFERENT information:

        - Journal.get_display_info() -> "Journal Week 3: Approved"
        - Evaluation.get_display_info() -> "Rating: 4.5/5 - Highly Recommended"

        Same method name, different behavior - that's POLYMORPHISM!

        Returns:
            str: Human-readable evaluation summary
        """
        return f"Rating: {self.overall_rating}/5 - {self.get_recommendation_display()}"

    def get_star_display(self, rating):
        """
        Convert numeric rating to star display.

        OOP Concept: HELPER METHOD
        -------------------------
        This private-ish method helps with display formatting.

        Args:
            rating: Numeric rating 1-5

        Returns:
            str: Star characters representing the rating
        """
        filled = int(rating)
        empty = 5 - filled
        return '★' * filled + '☆' * empty

    def get_work_quality_stars(self):
        """Get star display for work quality."""
        return self.get_star_display(self.work_quality)

    def get_attitude_stars(self):
        """Get star display for attitude."""
        return self.get_star_display(self.attitude)

    def get_overall_rating_stars(self):
        """Get star display for overall rating."""
        return self.get_star_display(self.overall_rating)

    def get_recommendation_badge_class(self):
        """
        Get Bootstrap badge class for recommendation.

        OOP Concept: ENCAPSULATION
        -------------------------
        Hides the mapping logic for CSS classes.

        Returns:
            str: Bootstrap badge class
        """
        badge_classes = {
            'recommended': 'badge-primary',
            'not_recommended': 'badge-danger',
            'highly_recommended': 'badge-success',
        }
        return badge_classes.get(self.recommendation, 'badge-secondary')

    def calculate_average(self):
        """
        Calculate average of work_quality and attitude.

        OOP Concept: COMPUTED PROPERTY
        ----------------------------
        Some data can be derived from other data.

        Returns:
            float: Average of the two ratings
        """
        return (self.work_quality + self.attitude) / 2

    def clean(self):
        """
        Validate evaluation data.

        Raises:
            ValidationError: If validation fails
        """
        from django.core.exceptions import ValidationError

        # Ensure supervisor can only evaluate students at their company
        if self.supervisor and self.student:
            from companies.models import Company
            supervisor_companies = Company.objects.filter(supervisor=self.supervisor)

            # Check if student is assigned to any of supervisor's companies
            from companies.models import Assignment
            valid_assignment = Assignment.objects.filter(
                student=self.student,
                company__in=supervisor_companies
            ).exists()

            if not valid_assignment:
                raise ValidationError(
                    "You can only evaluate students assigned to your company."
                )
