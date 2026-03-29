# OJT Management System - Class Diagram

## UML Class Diagram (Text-based)

```
+------------------+        +------------------+        +------------------+
|     User         |        |    Company       |        |   Assignment     |
+------------------+        +------------------+        +------------------+
| - username       |        | - name           |        | - start_date     |
| - email          |<-------| - address        |        | - end_date       |
| - password       |1     * | - supervisor     |------->| - required_hours |
| - role           |        | - contact_email  |   1  * +------------------+
| - profile_pic    |        +------------------+               |
| - phone          |               ^                           |
| - department     |               | 1                         |
+------------------+               |                           |
        ^                   +------+------+                    |
        |                   |             |                    |
        | 1                 |             |                    | *
        |            +------+------+      |                    |
+-------+-------+    |   DTRLog    |      |             +------+------+
|   |       |   |    +-------------+      |             |   Student   |
|   |       |   |    | - date      |      |             +-------------+
|   |       |   |<---| - time_in   |      |
|   |       |   | 1  | - time_out  |      |
|   |       |   |  * | - selfie    |      |
|   |       |   |    | - hours     |      |
|   |       |   |    +-------------+      |
|   |       |   |                         |
|   |       |   |    +-------------+      |
|   |       |   |    |   Journal   |      |
|   |       |   |<---+-------------+      |
|   |       |   | 1  | - week_num  |      |
|   |       |   |  * | - content   |      |
|   |       |   |    | - status    |      |
|   |       |   |    | - feedback  |      |
|   |       |   |    +-------------+      |
|   |       |   |                         |
|   |       |   |    +-------------+      |
|Teacher| |Supervisor+--| Evaluation |<----+
+-------+ +---------+   +-------------+
                    1 * | - work_qty  |
                        | - attitude  |
                        | - rating    |
                        | - recommend |
                        +-------------+
```

## Class Descriptions

### Abstract Base Class

**OJTBaseModel** (abstract)
- `created_at: DateTimeField`
- `updated_at: DateTimeField`
- `get_display_info()` [abstract method]
- `get_created_date_formatted()` [concrete method]

### User Model (extends AbstractUser)

**User**
- Inherits from: `AbstractUser` (Django built-in)
- Class Variables:
  - `ROLES: tuple` - Available role choices
- Instance Variables:
  - `role: CharField` - User's role (teacher/student/supervisor)
  - `profile_pic: ImageField` - Profile picture
  - `phone: CharField` - Contact number
  - `department: CharField` - Department/course

Methods:
- `__str__()` - String representation [overrides object.__str__]
- `get_full_name()` - Returns formatted full name [encapsulation]
- `get_role_display_label()` - Returns role with icon [encapsulation]
- `get_dashboard_url()` - Returns role-specific URL [polymorphism]
- `is_teacher()`, `is_student()`, `is_supervisor()` - Predicate methods

### Company Model

**Company**
- Instance Variables:
  - `name: CharField`
  - `address: TextField`
  - `supervisor: ForeignKey(User)` - Association

Methods:
- `__str__()` - Returns company name
- `get_supervisor_name()` - Encapsulated supervisor access
- `get_intern_count()` - Computed property

### Assignment Model (Association Class)

**Assignment**
- Represents relationship between Student and Company
- Class Variables:
  - `DEFAULT_REQUIRED_HOURS: int = 486`
- Instance Variables:
  - `student: ForeignKey(User)`
  - `company: ForeignKey(Company)`
  - `start_date: DateField`
  - `end_date: DateField`
  - `required_hours: FloatField`

Methods:
- `get_rendered_hours()` - Computed from DTR logs
- `get_progress_percentage()` - Derived data
- `is_active()` - Predicate method

### DTRLog Model

**DTRLog**
- Instance Variables:
  - `student: ForeignKey(User)`
  - `date: DateField`
  - `time_in: TimeField`
  - `time_out: TimeField`
  - `selfie: ImageField`
  - `hours_rendered: FloatField` - Auto-calculated

Methods:
- `save()` - Override for auto-calculation [encapsulation]
- `get_hours_rendered()` - Formatted output
- `is_complete()` - Predicate method

### Journal Model (extends OJTBaseModel)

**Journal**
- Inherits from: `OJTBaseModel` (abstract)
- Inherits: `created_at`, `updated_at` fields
- Class Variables:
  - `STATUS_CHOICES: tuple`
- Instance Variables:
  - `student: ForeignKey(User)`
  - `week_number: IntegerField`
  - `content: TextField`
  - `status: CharField`
  - `feedback: TextField`

Methods:
- `get_display_info()` - Implements abstract method
- `can_edit()`, `can_delete()` - Business logic
- `approve()`, `reject()` - State transition methods

### Evaluation Model (extends OJTBaseModel)

**Evaluation**
- Inherits from: `OJTBaseModel` (abstract)
- Class Variables:
  - `RECOMMENDATION_CHOICES: tuple`
  - `RATING_CHOICES: tuple`
- Instance Variables:
  - `supervisor: ForeignKey(User)`
  - `student: ForeignKey(User)`
  - `work_quality: IntegerField`
  - `attitude: IntegerField`
  - `overall_rating: FloatField`
  - `recommendation: CharField`
  - `notes: TextField`

Methods:
- `get_display_info()` - Implements abstract method
- `get_star_display()` - Helper method for star rendering

## Relationships (UML Notation)

1. **User (1) ----supervises----> (*) Company**
   - One supervisor can manage multiple companies
   - A company has one supervisor

2. **Company (1) <----assigned---- (*) Assignment**
   - One company can have multiple student assignments
   - Each assignment is to one company

3. **User (1) <----assigned---- (*) Assignment**
   - One student can have multiple assignments (over time)
   - Each assignment is for one student

4. **User (1) <----logs---- (*) DTRLog**
   - One student has many DTR logs
   - Each DTR log belongs to one student

5. **User (1) <----writes---- (*) Journal**
   - One student writes many journals
   - Each journal is written by one student

6. **User (Supervisor) (1) ----evaluates----> (*) Evaluation**
   - One supervisor can give many evaluations
   - Each evaluation is from one supervisor

7. **User (Student) (1) <----receives---- (*) Evaluation**
   - One student receives many evaluations
   - Each evaluation is for one student

## Inheritance Hierarchy

```
Python object
    |
    +-- models.Model (Django)
    |       |
    |       +-- OJTBaseModel (abstract)
    |       |       |
    |       |       +-- Journal
    |       |       +-- Evaluation
    |       |
    |       +-- Company
    |       +-- Assignment
    |       +-- DTRLog
    |
    +-- AbstractUser (Django)
            |
            +-- User (custom)

LoginRequiredMixin (Django)
    |
    +-- BaseRoleView
            |
            +-- TeacherRequiredMixin
            +-- StudentRequiredMixin
            +-- SupervisorRequiredMixin
```
