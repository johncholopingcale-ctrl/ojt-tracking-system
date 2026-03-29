# CRUD Operations Documentation

## OOP Concept: Database Integration (Topic 10)

This document shows how Django ORM maps Python objects to database tables and demonstrates CRUD (Create, Read, Update, Delete) operations.

---

## CREATE Operations

### Creating a new User
```python
# Django ORM maps this to: INSERT INTO accounts_user (...) VALUES (...)
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.create_user(
    username='john_doe',
    email='john@example.com',
    password='securepassword123',
    role='student',
    first_name='John',
    last_name='Doe'
)
```

### Creating an Assignment
```python
# View: AssignStudentView (CreateView)
# File: companies/views.py

from companies.models import Assignment

assignment = Assignment.objects.create(
    student=student_user,
    company=company,
    start_date='2024-01-15',
    end_date='2024-06-15',
    required_hours=486
)
```

### Creating a DTR Log
```python
# View: DTRLogCreateView (CreateView)
# File: dtr/views.py

from dtr.models import DTRLog

dtr_log = DTRLog.objects.create(
    student=request.user,
    date='2024-02-01',
    time_in='08:00:00',
    time_out='17:00:00',
    selfie=selfie_file
)
# hours_rendered is auto-calculated in save() method
```

### Creating a Journal
```python
# View: JournalCreateView (CreateView)
# File: journals/views.py

from journals.models import Journal

journal = Journal.objects.create(
    student=request.user,
    week_number=1,
    content='This week I learned about...',
    status='pending'  # Default value
)
```

### Creating an Evaluation
```python
# View: EvaluationCreateView (CreateView)
# File: evaluations/views.py

from evaluations.models import Evaluation

evaluation = Evaluation.objects.create(
    supervisor=request.user,
    student=student,
    work_quality=4,
    attitude=5,
    overall_rating=4.5,
    recommendation='highly_recommended',
    notes='Excellent performance...'
)
```

---

## READ Operations

### Reading all students
```python
# View: TeacherDashboardView
# File: companies/views.py

# Django ORM maps this to: SELECT * FROM accounts_user WHERE role='student'
students = User.objects.filter(role='student')
```

### Reading with related objects (JOIN)
```python
# Getting DTR logs with student info
# Maps to: SELECT ... FROM dtr_dtrlog JOIN accounts_user ON ...
dtr_logs = DTRLog.objects.select_related('student').filter(student_id=student_id)
```

### Aggregation queries
```python
# Calculating total hours
# Maps to: SELECT SUM(hours_rendered) FROM dtr_dtrlog WHERE student_id=...
from django.db.models import Sum

total_hours = DTRLog.objects.filter(
    student=student
).aggregate(total=Sum('hours_rendered'))['total'] or 0
```

### Filtering with multiple conditions
```python
# Getting pending journals
journals = Journal.objects.filter(
    student=request.user,
    status='pending'
).order_by('-submitted_at')
```

### Reading a single object
```python
# View: JournalReviewView
# Maps to: SELECT * FROM journals_journal WHERE id=...
from django.shortcuts import get_object_or_404

journal = get_object_or_404(Journal, pk=pk)
```

---

## UPDATE Operations

### Updating with form (UpdateView)
```python
# View: EditAssignmentView (UpdateView)
# File: companies/views.py

# Django handles the UPDATE automatically when form.save() is called
# Maps to: UPDATE companies_assignment SET ... WHERE id=...

class EditAssignmentView(TeacherRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm

    def form_valid(self, form):
        # form.save() executes the UPDATE query
        response = super().form_valid(form)
        return response
```

### Manual update
```python
# Approving a journal
# View: JournalReviewView
# File: companies/views.py

journal = Journal.objects.get(pk=pk)
journal.status = 'approved'
journal.feedback = 'Great work!'
journal.save()  # Executes UPDATE query
```

### Bulk update
```python
# Update all pending journals for a student
Journal.objects.filter(
    student=student,
    status='pending'
).update(status='approved')
```

---

## DELETE Operations

### Deleting with DeleteView
```python
# View: DeleteAssignmentView (DeleteView)
# File: companies/views.py

# Maps to: DELETE FROM companies_assignment WHERE id=...

class DeleteAssignmentView(TeacherRequiredMixin, DeleteView):
    model = Assignment
    success_url = reverse_lazy('teacher:dashboard')

    def delete(self, request, *args, **kwargs):
        # super().delete() executes the DELETE query
        return super().delete(request, *args, **kwargs)
```

### Manual delete
```python
# Deleting a DTR log
dtr_log = DTRLog.objects.get(pk=pk, student=request.user)
dtr_log.delete()  # Executes DELETE query
```

### Safe delete with ownership check
```python
# Only delete if the object belongs to the user
# This is how we enforce data isolation
def get_queryset(self):
    return DTRLog.objects.filter(student=self.request.user)
```

---

## Django ORM to SQL Mapping

| Django ORM | SQL Equivalent |
|------------|----------------|
| `Model.objects.create(...)` | `INSERT INTO table (...) VALUES (...)` |
| `Model.objects.all()` | `SELECT * FROM table` |
| `Model.objects.filter(field=value)` | `SELECT * FROM table WHERE field=value` |
| `Model.objects.get(pk=1)` | `SELECT * FROM table WHERE id=1` |
| `instance.save()` | `UPDATE table SET ... WHERE id=...` |
| `instance.delete()` | `DELETE FROM table WHERE id=...` |
| `Model.objects.aggregate(Sum('field'))` | `SELECT SUM(field) FROM table` |
| `Model.objects.select_related('fk')` | `SELECT ... JOIN ... ON ...` |

---

## OOP Principles in CRUD

1. **Encapsulation**: Database operations are encapsulated in Django's ORM layer
2. **Abstraction**: We work with Python objects, not raw SQL
3. **Object-Relational Mapping**: Each model class maps to a database table
4. **Instance = Row**: Each model instance represents a database row
5. **QuerySet = Result Set**: QuerySets represent database query results
