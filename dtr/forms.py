"""
DTR Forms - Forms for Daily Time Record Management

OOP Concept: FORM CLASSES
========================
Forms encapsulate data collection and validation.
"""

from django import forms
from django.utils import timezone
from datetime import date
from .models import DTRLog


class DTRLogInForm(forms.ModelForm):
    """
    Form for logging in (time_in only) with selfie capture.
    
    OOP Concept: SPECIALIZED FORM
    ----------------------------
    This form handles only log-in, creating a new DTR entry.
    """

    # Hidden field for base64 selfie data from webcam
    selfie_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = DTRLog
        fields = ['date', 'time_in', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'time_in': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about today\'s activities...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set today as default date
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
        # Set helpful labels
        self.fields['date'].label = 'Date'
        self.fields['time_in'].label = 'Log In Time'


class DTRLogOutForm(forms.ModelForm):
    """
    Form for logging out (time_out only).
    
    OOP Concept: SPECIALIZED FORM
    ----------------------------
    This form handles only log-out, updating existing DTR entry.
    """

    class Meta:
        model = DTRLog
        fields = ['time_out', 'notes']
        widgets = {
            'time_out': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about today\'s activities...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_out'].label = 'Log Out Time'

    def clean_time_out(self):
        """
        Validate that time_out is after time_in.
        """
        time_out = self.cleaned_data.get('time_out')
        if self.instance and self.instance.time_in:
            if time_out <= self.instance.time_in:
                raise forms.ValidationError(
                    "Log out time must be after log in time."
                )
        return time_out


class DTRLogForm(forms.ModelForm):
    """
    Form for logging DTR entries with selfie capture.

    OOP Concept: MODELFORM WITH CUSTOM FIELDS
    ----------------------------------------
    We add a hidden field for base64 selfie data that's not part of the model.
    The view will process this field and convert it to an image file.
    
    Date and time fields are now manual input for flexibility.
    """

    # Hidden field for base64 selfie data from webcam
    selfie_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = DTRLog
        fields = ['date', 'time_in', 'time_out', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'time_in': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'time_out': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about today\'s activities...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make time_out optional
        self.fields['time_out'].required = False
        # Set helpful labels
        self.fields['date'].label = 'Date'
        self.fields['time_in'].label = 'Time In'
        self.fields['time_out'].label = 'Time Out'

    def clean(self):
        """
        Validate time sequence.

        OOP Concept: FORM-LEVEL VALIDATION
        ---------------------------------
        clean() validates multiple fields together.
        """
        cleaned_data = super().clean()
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')

        if time_in and time_out:
            if time_out <= time_in:
                raise forms.ValidationError(
                    "Time out must be after time in."
                )

        return cleaned_data


class DTREditForm(forms.ModelForm):
    """
    Form for editing existing DTR entries.

    OOP Concept: SPECIALIZED FORM
    ----------------------------
    This form is used specifically for editing, with different
    fields than the creation form.
    """

    class Meta:
        model = DTRLog
        fields = ['date', 'time_in', 'time_out', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'time_in': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'time_out': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }

    def clean(self):
        """Validate time sequence."""
        cleaned_data = super().clean()
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')

        if time_in and time_out and time_out <= time_in:
            raise forms.ValidationError("Time out must be after time in.")

        return cleaned_data
