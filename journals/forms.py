"""
Journals Forms
"""

from django import forms
from .models import Journal


class JournalForm(forms.ModelForm):
    """
    Form for submitting weekly journals.

    OOP Concept: MODELFORM
    ---------------------
    Automatically creates form fields from model fields.
    """

    class Meta:
        model = Journal
        fields = ['week_number', 'content']
        widgets = {
            'week_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Week number'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your weekly reflection here... (minimum 50 characters)'
            }),
        }

    def clean_week_number(self):
        """Validate week number is positive."""
        week_number = self.cleaned_data.get('week_number')
        if week_number is not None and week_number < 1:
            raise forms.ValidationError("Week number must be at least 1.")
        return week_number

    def clean_content(self):
        """Validate content has minimum length."""
        content = self.cleaned_data.get('content', '')
        if len(content.strip()) < 50:
            raise forms.ValidationError("Journal content must be at least 50 characters.")
        return content


class JournalReviewForm(forms.Form):
    """
    Form for teachers to review journals.
    """

    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter feedback for the student...'
        })
    )

    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.HiddenInput()
    )
