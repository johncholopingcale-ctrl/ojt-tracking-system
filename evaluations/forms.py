"""
Evaluations Forms
"""

from django import forms
from .models import Evaluation


class EvaluationForm(forms.ModelForm):
    """
    Form for supervisor evaluations.

    OOP Concept: FORM WITH CUSTOM WIDGETS
    ------------------------------------
    Custom widgets are used for star rating selection.
    """

    class Meta:
        model = Evaluation
        fields = ['work_quality', 'attitude', 'overall_rating', 'recommendation', 'notes']
        widgets = {
            'work_quality': forms.Select(attrs={
                'class': 'form-control star-rating',
            }),
            'attitude': forms.Select(attrs={
                'class': 'form-control star-rating',
            }),
            'overall_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5',
                'step': '0.5',
            }),
            'recommendation': forms.Select(attrs={
                'class': 'form-control',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional comments about the student\'s performance...'
            }),
        }

    def clean_overall_rating(self):
        """Validate overall rating is between 1 and 5."""
        rating = self.cleaned_data.get('overall_rating')
        if rating is not None:
            if rating < 1 or rating > 5:
                raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating
