# CHMSU OJT Tracking System

A comprehensive On-the-Job Training (OJT) Management System built with Django for tracking student internship progress, daily attendance, journals, and performance evaluations.

**Live Demo:** [https://chmsu-ojt-tracker.up.railway.app](https://chmsu-ojt-tracker.up.railway.app)

## Project Information

- **Institution:** Carlos Hilado Memorial State University
- **College:** College of Computer Studies
- **Program:** Bachelor of Science in Information Systems (BSIS)
- **Course:** Object-Oriented Programming
- **SDG Alignment:** SDG 9 - Industry, Innovation, and Infrastructure

---

## System Features

### 👨‍🏫 Teacher/Coordinator Features

| Feature | Description |
|---------|-------------|
| **Dashboard Overview** | View total students, companies, pending tasks, and quick statistics |
| **Student Management** | View list of all students with their OJT status and progress |
| **Company Assignment** | Assign students to partner companies for their OJT |
| **DTR Monitoring** | View all student DTR logs and attendance records |
| **Rejected DTR Overview** | View list of all rejected DTR logs across all students |
| **Journal Review** | Review, approve, or reject student weekly journals with feedback |
| **Evaluation Access** | View supervisor evaluations and student performance ratings |
| **Progress Tracking** | Monitor students' required hours vs. rendered hours |

### 👨‍🎓 Student Features

| Feature | Description |
|---------|-------------|
| **Personal Dashboard** | View OJT progress, hours rendered, and pending tasks |
| **Progress Bar** | Visual progress indicator showing completion percentage |
| **DTR Time-In** | Log daily attendance with webcam selfie capture and timestamp |
| **DTR Time-Out** | Record end of workday with logout selfie |
| **DTR History** | View all past DTR logs with status (pending, confirmed, rejected) |
| **DTR Resubmission** | Resubmit rejected DTRs with new photo and corrected information |
| **Rejected DTR Logs** | View archived history of rejected DTR submissions |
| **Weekly Journals** | Submit weekly reflection journals about OJT experiences |
| **Journal Management** | Edit pending journals, view approved/rejected status |
| **Evaluation View** | View performance evaluations submitted by supervisors |
| **Profile Management** | Update personal information and profile picture |

### 👨‍💼 Supervisor Features

| Feature | Description |
|---------|-------------|
| **Supervisor Dashboard** | Overview of assigned interns and pending confirmations |
| **Intern List** | View all interns assigned to their company |
| **DTR Verification** | Review and confirm/reject intern daily attendance |
| **Photo Verification** | View login/logout selfies to verify attendance |
| **Resubmission Review** | Verify resubmitted DTRs with new photos |
| **Rejection Feedback** | Provide reasons when rejecting DTR logs |
| **Performance Evaluation** | Submit comprehensive performance evaluations for interns |
| **Rating System** | Rate interns on work quality, attendance, attitude, and skills |

### 🔐 Authentication & Security

| Feature | Description |
|---------|-------------|
| **Role-Based Access** | Separate dashboards and permissions for each user role |
| **Login System** | Secure authentication with session management |
| **Registration** | New user registration with role selection |
| **Password Security** | Hashed passwords using Django's authentication |
| **CSRF Protection** | Cross-site request forgery protection on all forms |

### 📸 DTR (Daily Time Record) System

| Feature | Description |
|---------|-------------|
| **Webcam Capture** | Real-time selfie capture using device camera |
| **Timestamp Overlay** | Philippine time timestamp automatically added to photos |
| **Photo Storage** | Secure storage of attendance verification photos |
| **Hours Calculation** | Automatic calculation of hours rendered per day |
| **Status Tracking** | Track confirmation status (pending, confirmed, rejected) |
| **Rejection Handling** | View rejection reasons and resubmit with corrections |
| **History Archive** | Rejected DTRs archived for record-keeping |
| **Validity Flag** | Invalid/rejected time-ins marked as "Not Logged In" |

### 📓 Journal System

| Feature | Description |
|---------|-------------|
| **Weekly Submission** | Submit journals for each week of OJT |
| **Rich Text Content** | Describe activities, learnings, and reflections |
| **Status Workflow** | Pending → Approved/Rejected flow with teacher feedback |
| **Edit Capability** | Edit journals while still in pending status |
| **Feedback Display** | View teacher remarks and suggestions |

### 📊 Evaluation System

| Feature | Description |
|---------|-------------|
| **Comprehensive Rating** | Multiple criteria evaluation (quality, attitude, skills) |
| **Numeric Scoring** | 1-5 rating scale for objective assessment |
| **Written Feedback** | Supervisors can add detailed comments |
| **Recommendation** | Supervisors can recommend students for hire |
| **Historical Record** | All evaluations stored for future reference |

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 4.2+ (Python) |
| Database | PostgreSQL (Supabase) |
| Frontend | HTML5, CSS3, Bootstrap 4 |
| JavaScript | Vanilla JS (ES6+) |
| Image Processing | Pillow (PIL) |
| Forms | django-crispy-forms |
| Static Files | WhiteNoise |
| Deployment | Railway |
| Media Storage | Cloudinary (optional) |

---

## System Limitations

### 🚫 Current Limitations

| Category | Limitation |
|----------|------------|
| **Camera Access** | Requires HTTPS for webcam access (browser security requirement) |
| **Browser Support** | Best experience on Chrome, Firefox, Edge; limited on Safari |
| **Mobile Camera** | Mobile devices may have camera orientation issues |
| **Offline Mode** | No offline functionality - requires internet connection |
| **Real-time Updates** | No real-time notifications; requires page refresh |
| **Bulk Operations** | No bulk approval/rejection of DTRs or journals |
| **Export Features** | No PDF/Excel export of DTR records or reports |
| **Date Restrictions** | Students cannot log DTR for past dates (only current day) |
| **Single Company** | Students can only be assigned to one company at a time |
| **Photo Size** | Large selfie images may slow down loading on slow connections |

### ⚠️ Known Issues

| Issue | Description |
|-------|-------------|
| **Camera Permission** | Users must manually grant camera permissions |
| **Session Timeout** | Long sessions may require re-login |
| **Time Zone** | System uses Asia/Manila timezone only |
| **Concurrent Edits** | No conflict resolution for simultaneous edits |
| **Password Recovery** | Email-based password reset not fully configured |

### 🔮 Future Enhancements (Not Yet Implemented)

| Enhancement | Description |
|-------------|-------------|
| Email Notifications | Notify users of approvals, rejections, and deadlines |
| PDF Reports | Generate printable DTR and evaluation reports |
| Analytics Dashboard | Charts and graphs for progress visualization |
| Mobile App | Native mobile application for easier DTR logging |
| GPS Location | Location verification for attendance |
| QR Code Check-in | Alternative attendance method using QR codes |
| Multi-language Support | Support for Filipino and other languages |
| Dark Mode | Theme toggle for better accessibility |
| Bulk Import/Export | Import students via CSV, export records |
| Automated Reminders | Remind students to submit journals and log DTR |

---

## Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- PostgreSQL (or SQLite for development)

### Local Development Setup

1. **Clone or download the project**
   ```bash
   cd ojt_project
   ```

2. **Create a virtual environment**
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

4. **Set up environment variables** (create `.env` file)
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=your-database-url
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Seed the database with test data**
   ```bash
   python manage.py seed_data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and navigate to: `http://localhost:8000`

---

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

---

## URL Structure

| URL | Description | Role |
|-----|-------------|------|
| `/` | Home (redirects to dashboard) | All |
| `/accounts/login/` | Login page | All |
| `/accounts/register/` | Registration | All |
| `/teacher/dashboard/` | Teacher dashboard | Teacher |
| `/teacher/assign/` | Assign students | Teacher |
| `/teacher/journals/` | Review journals | Teacher |
| `/teacher/dtr/rejected/` | View rejected DTRs | Teacher |
| `/student/dashboard/` | Student dashboard | Student |
| `/student/dtr/` | DTR list | Student |
| `/student/dtr/log/` | Log new DTR | Student |
| `/student/dtr/<id>/resubmit/` | Resubmit rejected DTR | Student |
| `/student/dtr/history/` | View rejected DTR history | Student |
| `/student/journals/` | Journal list | Student |
| `/supervisor/dashboard/` | Supervisor dashboard | Supervisor |
| `/supervisor/interns/` | Intern list | Supervisor |
| `/supervisor/dtr/pending/` | Pending DTR confirmations | Supervisor |
| `/supervisor/dtr/<id>/confirm/` | Confirm/reject DTR | Supervisor |

---

## Admin Access

Create a superuser to access Django admin:
```bash
python manage.py createsuperuser
```

Access admin at: `http://localhost:8000/admin/`

---

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
│   ├── models.py          # DTRLog, DTRHistory models
│   └── views.py           # DTR views including resubmission
├── journals/              # Weekly journals app
├── evaluations/           # Evaluations app
├── templates/             # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── teacher/
│   ├── student/
│   └── supervisor/
├── static/                # Static files (CSS, JS)
├── media/                 # Uploaded files
│   ├── profiles/
│   └── selfies/
└── docs/                  # Documentation
```

---

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

---

## Deployment

This project is deployed on Railway with:
- **Database:** PostgreSQL on Supabase
- **Static Files:** WhiteNoise
- **Media Storage:** Cloudinary (optional)

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@host:port/db
ALLOWED_HOSTS=your-domain.railway.app
CSRF_TRUSTED_ORIGINS=https://your-domain.railway.app
```

---

## Contributing

This project is for educational purposes. Feel free to use it as a reference for learning OOP concepts with Django.

## License

This project is created for educational purposes at Carlos Hilado Memorial State University.

---

## Credits

- **Developers:** BSIS Students, CHMSU
- **Course:** Object-Oriented Programming
- **Academic Year:** 2025-2026
