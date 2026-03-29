# OJT Management System - Project Overview

## Project Information

**Project Title:** OJT Management System
**Institution:** Carlos Hilado Memorial State University
**College:** College of Computer Studies
**Program:** Bachelor of Science in Information Systems (BSIS)
**Course:** Object-Oriented Programming

---

## Project Domain: Education

This system is an educational management tool designed to track and manage On-the-Job Training (OJT) activities for students in the BSIS program.

### SDG Alignment: SDG 9 - Industry, Innovation, and Infrastructure

This project aligns with **Sustainable Development Goal 9: Industry, Innovation, and Infrastructure** because:

1. **Industry Connection**: Bridges the gap between academic learning and industry practice
2. **Innovation in Education**: Uses modern web technologies to improve training management
3. **Infrastructure for Learning**: Provides digital infrastructure for OJT tracking and evaluation

---

## System Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django (Python) |
| Database | SQLite |
| Frontend | HTML, CSS, Bootstrap 4 |
| JavaScript | Vanilla JS (for webcam) |
| Image Processing | Pillow |
| Forms | django-crispy-forms |
| Authentication | Django built-in + Custom User |

### Application Structure

```
ojt_project/
├── ojt_project/          # Main project configuration
│   ├── settings.py       # Configuration (OOP: Configuration class)
│   ├── urls.py           # URL routing (OOP: Delegation pattern)
│   ├── base_models.py    # Abstract base class (OOP: Abstraction)
│   └── exceptions.py     # Custom exceptions (OOP: Exception handling)
├── accounts/             # User management app
│   ├── models.py         # User model (OOP: Inheritance from AbstractUser)
│   ├── views.py          # Auth views (OOP: Class-based views)
│   ├── mixins.py         # Role mixins (OOP: Multiple inheritance)
│   └── utils.py          # FileHandler (OOP: Utility class)
├── companies/            # Company & assignment management
│   ├── models.py         # Company, Assignment (OOP: Association)
│   └── views.py          # Teacher views (OOP: View inheritance)
├── dtr/                  # Daily Time Records
│   ├── models.py         # DTRLog (OOP: Encapsulation in save())
│   └── views.py          # Student DTR views
├── journals/             # Weekly journals
│   ├── models.py         # Journal (OOP: Inherits OJTBaseModel)
│   └── views.py          # Journal CRUD views
├── evaluations/          # Performance evaluations
│   ├── models.py         # Evaluation (OOP: Inherits OJTBaseModel)
│   └── views.py          # Supervisor views
└── templates/            # HTML templates
    ├── base.html         # Base template (OOP: Template inheritance)
    ├── teacher/          # Teacher-specific templates
    ├── student/          # Student-specific templates
    └── supervisor/       # Supervisor-specific templates
```

---

## OOP Concepts Demonstrated

### Topic 1: Introduction to OOP

**Location:** All Python files

The entire project demonstrates OOP principles:
- **Classes** represent real-world entities (User, Company, Journal, etc.)
- **Objects** are instances of these classes (each user, each journal entry)
- **Contrast with Procedural**: Instead of separate data structures and functions, we bundle data and behavior together in classes

### Topic 2: Classes and Objects

**Location:** All `models.py` files

- **Class Definition**: Each model (User, Company, DTRLog, etc.)
- **Instance Variables**: Model fields (username, email, etc.)
- **Class Variables**: Choice tuples (ROLES, STATUS_CHOICES)
- **Object Instantiation**: Creating model instances (`User.objects.create()`)

### Topic 3: Encapsulation

**Location:** `dtr/models.py`, `accounts/models.py`

- `DTRLog.save()` encapsulates hours calculation
- `User.get_full_name()` encapsulates name formatting
- `Journal.can_edit()` encapsulates business rules

### Topic 4: Inheritance

**Location:** `accounts/mixins.py`, templates

- **Single Inheritance**: `User(AbstractUser)`, `BaseRoleView(LoginRequiredMixin)`
- **Multilevel Inheritance**: `TeacherRequiredMixin -> BaseRoleView -> LoginRequiredMixin`
- **Template Inheritance**: `dashboard.html -> base_teacher.html -> base.html`

### Topic 5: Polymorphism

**Location:** `accounts/models.py`, views

- `User.get_dashboard_url()` returns different URLs based on role
- `__str__()` method is overridden in every model
- `get_context_data()` is overridden in every view

### Topic 6: Abstraction

**Location:** `ojt_project/base_models.py`

- `OJTBaseModel` is an abstract class
- Cannot be instantiated directly
- `get_display_info()` is an abstract method implemented by Journal and Evaluation

### Topic 7: File Handling

**Location:** `accounts/utils.py`, `dtr/views.py`

- `FileHandler` class for image processing
- Webcam selfie capture and base64 conversion
- Profile picture and selfie uploads

### Topic 8: Exception Handling

**Location:** `ojt_project/exceptions.py`, all views

- Custom `OJTValidationError`, `OJTPermissionError`, `OJTNotFoundError`
- All views wrap operations in try-except blocks
- Exceptions inherit from base `OJTBaseException`

### Topic 9: OOP Design and UML

**Location:** `docs/class_diagram.md`

- Text-based UML class diagram
- Relationships documented (1-to-many, many-to-many)
- SOLID principles applied throughout

### Topic 10: Database Integration

**Location:** `docs/crud_examples.md`, all views

- Django ORM demonstrates object-relational mapping
- CRUD operations documented with SQL equivalents
- QuerySets represent result sets

### Topic 11: GUI Programming

**Location:** `templates/`

- Bootstrap 4 templates serve as GUI layer
- Responsive design
- Interactive elements (webcam capture)

### Topic 12: Final Project

This project integrates all OOP concepts into a functional system:
- **Domain**: Education (OJT Management)
- **SDG**: 9 - Industry, Innovation, Infrastructure
- **Functionality**: Complete CRUD, role-based access, file handling

---

## SOLID Principles in This Project

### Single Responsibility Principle (SRP)
- Each app handles one domain (accounts, companies, dtr, journals, evaluations)
- Each view handles one operation
- Each model represents one entity

### Open/Closed Principle (OCP)
- Mixin system is open for extension (new roles can be added)
- Views extend generic views without modifying them

### Liskov Substitution Principle (LSP)
- TeacherRequiredMixin can substitute BaseRoleView
- Journal and Evaluation can substitute OJTBaseModel references

### Interface Segregation Principle (ISP)
- Each role has its own views and templates
- No role is forced to implement unnecessary interfaces

### Dependency Inversion Principle (DIP)
- Views depend on abstract mixins, not concrete implementations
- Models depend on abstract OJTBaseModel

---

## User Roles and Permissions

| Feature | Teacher | Student | Supervisor |
|---------|---------|---------|------------|
| View Dashboard | ✓ | ✓ | ✓ |
| Assign Students | ✓ | ✗ | ✗ |
| Log DTR | ✗ | ✓ | ✗ |
| Submit Journals | ✗ | ✓ | ✗ |
| Review Journals | ✓ | ✗ | ✗ |
| View DTR (Own) | ✗ | ✓ | ✗ |
| View DTR (Interns) | ✓ | ✗ | ✓ |
| Add Evaluations | ✗ | ✗ | ✓ |
| View Evaluations | ✓ | ✓ (own) | ✗ |
| Update Profile | ✗ | ✓ | ✗ |

---

## Data Flow

1. **Student Registration** → Creates User with role='student'
2. **Teacher Assignment** → Creates Assignment linking Student to Company
3. **Daily DTR Logging** → Student creates DTRLog with selfie
4. **Weekly Journal** → Student submits Journal for review
5. **Teacher Review** → Teacher approves/rejects Journal
6. **Supervisor Evaluation** → Supervisor creates Evaluation for Student
7. **Progress Tracking** → System calculates hours and progress percentage
