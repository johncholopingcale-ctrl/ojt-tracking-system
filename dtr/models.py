"""
DTR App - Daily Time Records

OOP Concept Demonstrated: CLASSES AND ENCAPSULATION (TOPIC 2 & 3)
=======================================================================
This file demonstrates key OOP concepts:
1. Class definition with instance attributes and methods
2. Encapsulation through the save() method that hides hours calculation logic
3. Method overriding with the custom save() method

The DTRLog class represents a real-world entity: a daily attendance record
that tracks when a student checks in and out of their OJT.
=======================================================================
"""

from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, date

from ojt_project.exceptions import OJTValidationError

User = get_user_model()


class DTRLog(models.Model):
    """
    Daily Time Record Log for tracking student attendance.

    OOP Concept: CLASS WITH CUSTOM SAVE METHOD
    -----------------------------------------
    This class demonstrates ENCAPSULATION by hiding the hours calculation
    logic inside the save() method. External code doesn't need to know
    HOW hours are calculated - they just save the object and it happens.

    Real-world entity: A student's daily attendance record
    ----------------------------------------------------
    - student: Who clocked in
    - date: What day
    - time_in: Clock-in time
    - time_out: Clock-out time
    - selfie: Photo taken at clock-in for verification
    - hours_rendered: Automatically calculated

    ENCAPSULATION example:
    ---------------------
    The hours_rendered calculation is ENCAPSULATED in the save() method.
    Instead of:
        dtr.hours_rendered = calculate_hours(dtr.time_in, dtr.time_out)
        dtr.save()

    We have:
        dtr.save()  # Hours calculated automatically

    This hides the implementation detail from external code.
    """

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dtr_logs',
        limit_choices_to={'role': 'student'},
        help_text="Student who logged this DTR"
    )

    date = models.DateField(
        help_text="Date of the DTR entry"
    )

    time_in = models.TimeField(
        help_text="Clock-in time"
    )

    time_out = models.TimeField(
        null=True,
        blank=True,
        help_text="Clock-out time (can be logged later)"
    )

    selfie = models.ImageField(
        upload_to='selfies/%Y/%m/',
        help_text="Selfie taken at clock-in for verification"
    )

    logout_selfie = models.ImageField(
        upload_to='selfies/%Y/%m/',
        null=True,
        blank=True,
        help_text="Selfie taken at clock-out for verification"
    )

    hours_rendered = models.FloatField(
        default=0,
        help_text="Hours worked (auto-calculated from time_in and time_out)"
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional notes about the day's activities"
    )

    # Supervisor confirmation status
    CONFIRMATION_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    )

    confirmation_status = models.CharField(
        max_length=20,
        choices=CONFIRMATION_STATUS,
        default='pending',
        help_text="Supervisor confirmation status for this DTR log"
    )

    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_dtr_logs',
        limit_choices_to={'role': 'supervisor'},
        help_text="Supervisor who confirmed/rejected this log"
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the log was confirmed/rejected"
    )

    confirmation_remarks = models.TextField(
        blank=True,
        help_text="Supervisor's remarks for confirmation/rejection"
    )

    is_valid = models.BooleanField(
        default=True,
        help_text="Whether this time-in is valid. Set to False when DTR is rejected."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'DTR Log'
        verbose_name_plural = 'DTR Logs'
        ordering = ['-date', '-time_in']
        # Prevent duplicate entries for same student on same date
        unique_together = [['student', 'date']]

    def __str__(self):
        """
        String representation of the DTR log.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        Overrides __str__ from object class.
        """
        return f"{self.student.username} - {self.date}"

    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate hours_rendered.

        OOP Concept: ENCAPSULATION
        -------------------------
        This method ENCAPSULATES the hours calculation logic.
        The calculation happens automatically when saving.

        External code doesn't need to know:
        1. The formula for calculating hours
        2. How to handle missing time_out
        3. Edge cases like overtime

        They just call save() and it works.

        Exception Handling:
        ------------------
        We validate that time_out is not before time_in.
        """
        # Validate time sequence
        if self.time_in and self.time_out:
            if self.time_out <= self.time_in:
                raise OJTValidationError(
                    "Time out cannot be before or equal to time in.",
                    "INVALID_TIME_SEQUENCE"
                )

        # Auto-calculate hours rendered using accurate calculation
        if self.time_in and self.time_out:
            # Use the actual date from the record for accurate calculation
            record_date = self.date if self.date else date.today()
            t1 = datetime.combine(record_date, self.time_in)
            t2 = datetime.combine(record_date, self.time_out)
            
            # Calculate difference in hours (total_seconds / 3600)
            difference_seconds = (t2 - t1).total_seconds()
            hours = difference_seconds / 3600
            
            # Round to 2 decimal places for accuracy
            self.hours_rendered = round(hours, 2)
        elif not self.time_out:
            # No time_out yet - hours will be 0
            self.hours_rendered = 0

        super().save(*args, **kwargs)

    def get_hours_rendered(self):
        """
        Get formatted hours rendered.

        OOP Concept: ENCAPSULATION
        -------------------------
        This method controls HOW the hours data is exposed.
        Instead of directly accessing self.hours_rendered,
        external code calls this method for formatted output.

        Returns:
            str: Formatted hours string like "8.5 hours"
        """
        hours = self.hours_rendered
        if hours == 1:
            return "1 hour"
        elif hours < 1:
            return f"{int(hours * 60)} minutes"
        else:
            return f"{hours:.1f} hours"

    def get_time_in_formatted(self):
        """Get formatted time in string."""
        return self.time_in.strftime("%I:%M %p") if self.time_in else "Not logged"

    def get_time_out_formatted(self):
        """Get formatted time out string."""
        return self.time_out.strftime("%I:%M %p") if self.time_out else "Not logged"

    def is_complete(self):
        """
        Check if this DTR log has both time_in and time_out.

        OOP Concept: PREDICATE METHOD
        ----------------------------
        Returns boolean indicating if the record is complete.

        Returns:
            bool: True if both times are logged
        """
        return self.time_in is not None and self.time_out is not None

    def is_confirmed(self):
        """Check if this DTR log has been confirmed by supervisor."""
        return self.confirmation_status == 'confirmed'

    def is_pending_confirmation(self):
        """Check if this DTR log is pending supervisor confirmation."""
        return self.confirmation_status == 'pending'

    def is_rejected(self):
        """Check if this DTR log was rejected by supervisor."""
        return self.confirmation_status == 'rejected'

    def get_confirmation_status_display_label(self):
        """Get styled display label for confirmation status."""
        status_labels = {
            'pending': '⏳ Pending',
            'confirmed': '✅ Confirmed',
            'rejected': '❌ Rejected',
        }
        return status_labels.get(self.confirmation_status, self.get_confirmation_status_display())

    def clean(self):
        """
        Validate the DTR log before saving.

        OOP Concept: VALIDATION METHOD
        -----------------------------
        Django calls this during form validation.

        Raises:
            ValidationError: If validation fails
        """
        from django.core.exceptions import ValidationError

        if self.time_in and self.time_out:
            if self.time_out < self.time_in:
                raise ValidationError({
                    'time_out': 'Time out must be after time in.'
                })

        # Check for duplicate entries (same student, same date)
        if self.pk is None:  # New record
            existing = DTRLog.objects.filter(
                student=self.student,
                date=self.date
            ).exists()
            if existing:
                raise ValidationError(
                    "A DTR log already exists for this date."
                )


class DTRHistory(models.Model):
    """
    History of DTR submissions, especially tracking rejected DTRs.
    
    When a DTR is rejected and the student resubmits, the rejected DTR
    is moved here to maintain a complete audit trail.
    """
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dtr_history',
        limit_choices_to={'role': 'student'},
        help_text="Student who submitted this DTR"
    )
    
    date = models.DateField(
        help_text="Date of the DTR entry"
    )
    
    time_in = models.TimeField(
        help_text="Clock-in time"
    )
    
    time_out = models.TimeField(
        null=True,
        blank=True,
        help_text="Clock-out time"
    )
    
    selfie = models.ImageField(
        upload_to='selfies/%Y/%m/',
        help_text="Selfie taken at clock-in"
    )
    
    logout_selfie = models.ImageField(
        upload_to='selfies/%Y/%m/',
        null=True,
        blank=True,
        help_text="Selfie taken at clock-out"
    )
    
    hours_rendered = models.FloatField(
        default=0,
        help_text="Hours worked"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notes about the day's activities"
    )
    
    # Confirmation fields
    confirmation_status = models.CharField(
        max_length=20,
        help_text="Status when archived (usually 'rejected')"
    )
    
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_dtr_history',
        help_text="Supervisor who confirmed/rejected this log"
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the log was confirmed/rejected"
    )
    
    confirmation_remarks = models.TextField(
        blank=True,
        help_text="Supervisor's remarks for rejection"
    )
    
    # Original DTR timestamps
    original_created_at = models.DateTimeField(
        help_text="When the original DTR was created"
    )
    
    original_updated_at = models.DateTimeField(
        help_text="When the original DTR was last updated"
    )
    
    # History entry metadata
    archived_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this entry was moved to history"
    )
    
    archived_reason = models.CharField(
        max_length=50,
        default='resubmission',
        help_text="Reason for archiving (e.g., 'resubmission')"
    )
    
    class Meta:
        verbose_name = 'DTR History'
        verbose_name_plural = 'DTR Histories'
        ordering = ['-date', '-archived_at']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['confirmation_status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.date} (Archived: {self.archived_at.strftime('%Y-%m-%d')})"
    
    @classmethod
    def archive_dtr(cls, dtr_log, reason='resubmission'):
        """
        Archive a DTR log to history.
        
        Args:
            dtr_log: DTRLog instance to archive
            reason: Reason for archiving
            
        Returns:
            DTRHistory instance
        """
        history_entry = cls.objects.create(
            student=dtr_log.student,
            date=dtr_log.date,
            time_in=dtr_log.time_in,
            time_out=dtr_log.time_out,
            selfie=dtr_log.selfie,
            logout_selfie=dtr_log.logout_selfie,
            hours_rendered=dtr_log.hours_rendered,
            notes=dtr_log.notes,
            confirmation_status=dtr_log.confirmation_status,
            confirmed_by=dtr_log.confirmed_by,
            confirmed_at=dtr_log.confirmed_at,
            confirmation_remarks=dtr_log.confirmation_remarks,
            original_created_at=dtr_log.created_at,
            original_updated_at=dtr_log.updated_at,
            archived_reason=reason
        )
        return history_entry
