# OJT Management System

A comprehensive On-the-Job Training (OJT) Management System built with Django, demonstrating Object-Oriented Programming concepts for the BSIS program at Carlos Hilado Memorial State University.

## Project Information

- **Institution:** Carlos Hilado Memorial State University
- **College:** College of Computer Studies
- **Program:** Bachelor of Science in Information Systems (BSIS)
- **Course:** Object-Oriented Programming
- **SDG Alignment:** SDG 9 - Industry, Innovation, and Infrastructure

## Features

### Teacher Features
- Dashboard with student overview
- Assign students to companies
- View student DTR logs
- Review and approve/reject journals
- View supervisor evaluations

### Student Features
- OJT progress tracking with visual progress bar
- Daily Time Record (DTR) logging with webcam selfie capture
- Weekly journal submission
- View evaluations from supervisors
- Profile management

### Supervisor Features
- View assigned interns
- View intern DTR logs
- Submit performance evaluations
- Rate work quality, attitude, and provide recommendations

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 4.2+ (Python) |
| Database | SQLite |
| Frontend | HTML, CSS, Bootstrap 4 |
| JavaScript | Vanilla JS |
| Image Processing | Pillow |
| Forms | django-crispy-forms |

## Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd ojt_project
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Seed the database with test data**
   ```bash
   python manage.py seed_data
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to: `http://localhost:8000`

## Test Accounts

After running `seed_data`, use these accounts:

| Role | Username | Password |
|------|----------|----------|
| Teacher | teacher1 | teacher123 |
| Supervisor | supervisor1 | supervisor123 |
| Supervisor | supervisor2 | supervisor123 |
| Student | student1 | student123 |
| Student | student2 | student123 |
| Student | student3 | student123 |

## OOP Concepts Demonstrated

| Topic | Concept | File Location |
|-------|---------|---------------|
| 1 | Introduction to OOP | All models.py files |
| 2 | Classes and Objects | `accounts/models.py`, all models |
| 3 | Encapsulation | `dtr/models.py` (save method), `accounts/models.py` |
| 4 | Inheritance | `accounts/mixins.py`, templates |
| 5 | Polymorphism | `accounts/models.py` (get_dashboard_url) |
| 6 | Abstraction | `ojt_project/base_models.py` |
| 7 | File Handling | `accounts/utils.py`, `dtr/views.py` |
| 8 | Exception Handling | `ojt_project/exceptions.py` |
| 9 | OOP Design & UML | `docs/class_diagram.md` |
| 10 | Database Integration | `docs/crud_examples.md`, all views |
| 11 | GUI Programming | `templates/` directory |
| 12 | Final Project | This complete system |

## Project Structure

```
ojt_project/
├── manage.py
├── requirements.txt
├── README.md
├── ojt_project/           # Main project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── base_models.py     # Abstract base class
│   └── exceptions.py      # Custom exceptions
├── accounts/              # User authentication app
│   ├── models.py          # Custom User model
│   ├── views.py           # Auth views
│   ├── mixins.py          # Role-based access mixins
│   └── utils.py           # File handling utilities
├── companies/             # Company & assignment app
├── dtr/                   # Daily Time Records app
├── journals/              # Weekly journals app
├── evaluations/           # Evaluations app
├── templates/             # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── teacher/
│   ├── student/
│   └── supervisor/
├── media/                 # Uploaded files
│   ├── profiles/
│   └── selfies/
└── docs/                  # Documentation
    ├── class_diagram.md
    ├── crud_examples.md
    └── project_overview.md
```

## URL Structure

| URL | Description | Role |
|-----|-------------|------|
| `/` | Home (redirects to dashboard) | All |
| `/accounts/login/` | Login page | All |
| `/accounts/register/` | Registration | All |
| `/teacher/dashboard/` | Teacher dashboard | Teacher |
| `/teacher/assign/` | Assign students | Teacher |
| `/teacher/journals/` | Review journals | Teacher |
| `/student/dashboard/` | Student dashboard | Student |
| `/student/dtr/` | DTR list | Student |
| `/student/dtr/log/` | Log new DTR | Student |
| `/student/journals/` | Journal list | Student |
| `/supervisor/dashboard/` | Supervisor dashboard | Supervisor |
| `/supervisor/interns/` | Intern list | Supervisor |

## Admin Access

Create a superuser to access Django admin:
```bash
python manage.py createsuperuser
```

Access admin at: `http://localhost:8000/admin/`

## Contributing

This project is for educational purposes. Feel free to use it as a reference for learning OOP concepts with Django.

## License

This project is created for educational purposes at Carlos Hilado Memorial State University.
