"""
Accounts Forms - User Registration and Authentication Forms

OOP Concept Demonstrated: FORM CLASSES AND INHERITANCE
=======================================================================
Django forms are classes that demonstrate key OOP principles:
1. Inheritance: Our forms inherit from Django's built-in form classes
2. Encapsulation: Form logic (validation, cleaning) is encapsulated
3. Abstraction: Complex form handling is abstracted behind simple interfaces

Form inheritance hierarchy:
    forms.Form (basic form)
        |
    forms.ModelForm (model-bound form)
        |
    UserCreationForm (user registration)
        |
    CustomUserCreationForm (our customization)
=======================================================================
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

# Filipino phone number validator
phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='Phone number must be in format: 09XXXXXXXXX (11 digits starting with 09)'
)


class CustomUserCreationForm(UserCreationForm):
    """
    Registration form for new users with role selection.

    OOP Concept: FORM INHERITANCE
    ----------------------------
    This class INHERITS from UserCreationForm, which provides:
    - Username field
    - Password1 and password2 fields (with validation)
    - User creation logic

    We EXTEND it by:
    - Adding role field (teacher, student, supervisor)
    - Adding email, first_name, last_name fields
    - Customizing widgets with Bootstrap classes

    This is INHERITANCE with EXTENSION - adding new features to parent class.
    """

    role = forms.ChoiceField(
        choices=User.ROLES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_role'
        }),
        help_text="Select your role in the OJT system"
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    company = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company/Organization name'
        }),
        help_text="Required for supervisors"
    )

    department = forms.CharField(
        max_length=100,
        required=False,
        label='Course/Program',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., BSIS, BSIT, BSCS'
        }),
        help_text="Required for students"
    )

    phone = forms.CharField(
        max_length=11,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09XXXXXXXXX',
            'pattern': '09[0-9]{9}',
            'title': 'Phone number must be 11 digits starting with 09'
        }),
        help_text="Filipino mobile number format: 09XXXXXXXXX"
    )

    class Meta:
        """
        Meta class configuring the form's model binding.

        OOP Concept: INNER CLASS / NESTED CLASS
        --------------------------------------
        Meta is a nested class that provides configuration for the parent class.
        This is a Django convention for separating configuration from behavior.
        """
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'department', 'company', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with Bootstrap-styled widgets.

        OOP Concept: CONSTRUCTOR CUSTOMIZATION
        -------------------------------------
        We override __init__ to customize widget attributes.
        The super().__init__() call ensures parent initialization runs first.
        """
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

        # Custom placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    def clean_email(self):
        """
        Validate that the email is unique.

        OOP Concept: VALIDATION METHOD
        -----------------------------
        Django forms use clean_<fieldname> methods for field-specific validation.
        This is a convention that demonstrates the TEMPLATE METHOD pattern.

        Returns:
            str: Validated email

        Raises:
            ValidationError: If email already exists
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        """
        Validate that company is provided for supervisors and department for students/teachers.
        """
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company = cleaned_data.get('company')
        department = cleaned_data.get('department')

        if role == 'supervisor' and not company:
            self.add_error('company', 'Company name is required for supervisors.')

        if role == 'student' and not department:
            self.add_error('department', 'Course/Program is required for students.')

        if role == 'teacher' and not department:
            self.add_error('department', 'Program/Course is required for coordinators.')

        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    """
    Login form with Bootstrap styling.

    OOP Concept: FORM INHERITANCE FOR STYLING
    ----------------------------------------
    We inherit from AuthenticationForm just to add Bootstrap classes.
    The authentication logic remains unchanged - this is INHERITANCE
    for EXTENSION without modification.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.

    OOP Concept: MODEL FORM
    ----------------------
    ModelForm automatically creates form fields from model fields.
    This demonstrates ABSTRACTION - the complex mapping between
    models and forms is hidden behind a simple interface.

    We just specify which model and fields, Django handles:
    - Creating appropriate form fields
    - Validation based on model field constraints
    - Saving data to the model instance
    """

    phone = forms.CharField(
        max_length=11,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09XXXXXXXXX',
            'pattern': '09[0-9]{9}',
            'title': 'Phone number must be 11 digits starting with 09'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'department', 'profile_pic')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department/Course'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_email(self):
        """
        Validate email uniqueness excluding current user.

        OOP Concept: CONTEXT-AWARE VALIDATION
        -----------------------------------
        This demonstrates how methods can use instance state (self.instance)
        to make context-aware decisions.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email


class SupervisorProfileForm(forms.ModelForm):
    """
    Form for updating supervisor profile information.
    Excludes department field as it should be read-only from registration.
    """

    phone = forms.CharField(
        max_length=11,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09XXXXXXXXX',
            'pattern': '09[0-9]{9}',
            'title': 'Phone number must be 11 digits starting with 09'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'profile_pic')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_email(self):
        """Validate email uniqueness excluding current user."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email
