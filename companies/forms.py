"""
Companies Forms - Forms for Company and Assignment Management

OOP Concept: FORM CLASSES
========================
Forms encapsulate data validation and presentation logic.
"""

from django import forms
from django.contrib.auth import get_user_model
from .models import Company, Assignment

User = get_user_model()


class CompanyForm(forms.ModelForm):
    """
    Form for creating/editing companies.

    OOP Concept: MODELFORM INHERITANCE
    ---------------------------------
    ModelForm inherits from Form and adds model binding.
    """

    class Meta:
        model = Company
        fields = ['name', 'address', 'supervisor', 'contact_email', 'contact_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show supervisors who have first and last name set
        supervisors = User.objects.filter(
            role='supervisor'
        ).exclude(first_name='').exclude(last_name='')
        self.fields['supervisor'].queryset = supervisors
        # Display full name instead of username
        self.fields['supervisor'].label_from_instance = lambda obj: obj.get_full_name()


class AssignmentForm(forms.ModelForm):
    """
    Form for creating/editing student assignments.

    OOP Concept: FORM WITH CUSTOM QUERYSET
    -------------------------------------
    We customize the queryset for related fields to show only
    relevant choices (students for student field).
    """

    class Meta:
        model = Assignment
        fields = ['student', 'company', 'start_date', 'end_date', 'required_hours']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'required_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show students who have first and last name set
        students = User.objects.filter(
            role='student'
        ).exclude(first_name='').exclude(last_name='')
        self.fields['student'].queryset = students
        # Display full name instead of username
        self.fields['student'].label_from_instance = lambda obj: obj.get_full_name()

    def clean(self):
        """
        Validate that end_date is after start_date and required_hours is positive.

        OOP Concept: FORM-LEVEL VALIDATION
        ---------------------------------
        clean() runs after individual field validation.
        It can validate fields in combination.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        required_hours = cleaned_data.get('required_hours')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date must be after start date.")

        if required_hours is not None and required_hours <= 0:
            raise forms.ValidationError("Required hours must be a positive number.")

        return cleaned_data
