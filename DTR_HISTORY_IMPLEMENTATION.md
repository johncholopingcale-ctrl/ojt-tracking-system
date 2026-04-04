# DTR History Feature Implementation Guide

## Overview
The DTR History feature allows students to view archived DTR logs, especially rejected ones, and resubmit them after making corrections.

## Files Involved

### 1. Migration File
- **File**: `dtr/migrations/0004_add_dtr_history.py`
- **Status**: ✅ Created
- **Purpose**: Creates the `DTRHistory` model in the database

### 2. Model (Already Implemented)
- **File**: `dtr/models.py`
- **Lines**: 297-437
- **Status**: ✅ Already exists
- **Class**: `DTRHistory`
- **Key Features**:
  - Stores archived DTR submissions
  - Tracks rejection reasons and supervisor remarks
  - Maintains full audit trail with original timestamps
  - Has a class method `archive_dtr()` to archive DTR logs

### 3. Views (Already Implemented)
- **File**: `dtr/views.py`
- **Status**: ✅ Already exists

#### DTRHistoryView (Lines 533-550)
- **Purpose**: List all archived DTR history for the current student
- **URL**: `/student/dtr/history/`
- **Template**: `templates/student/dtr_history.html`
- **Features**:
  - Paginated list of archived DTRs
  - Shows all history entries with full details

#### DTRResubmitView (Lines 448-531)
- **Purpose**: Resubmit a rejected DTR
- **URL**: `/student/dtr/<pk>/resubmit/`
- **Template**: `templates/student/dtr_resubmit.html`
- **Features**:
  - Archives rejected DTR to history
  - Creates new DTR with pending status
  - Allows editing time_in, time_out, notes
  - Supports capturing new selfies

### 4. Templates
- **Files**: 
  - `templates/student/dtr_history.html` ✅ Created
  - `templates/student/dtr_resubmit.html` ✅ Created
- **Status**: ✅ Both templates exist

#### dtr_history.html Features:
- Paginated table view of archived DTRs
- Shows date, time in/out, hours, status
- View details modal with full information
- Displays supervisor remarks for rejections
- Shows original and archived timestamps

#### dtr_resubmit.html Features:
- Shows rejection reason and supervisor remarks
- Form to edit time_in and time_out
- Webcam capture for new selfies
- Option to update notes
- Displays current selfies for reference

### 5. URLs (Already Configured)
- **File**: `dtr/urls_student.py`
- **Lines**: 26-27
- **Status**: ✅ Already configured
- **Routes**:
  ```python
  path('dtr/<int:pk>/resubmit/', views.DTRResubmitView.as_view(), name='dtr_resubmit'),
  path('dtr/history/', views.DTRHistoryView.as_view(), name='dtr_history'),
  ```

## How to Apply the Migration

### Method 1: Using Django manage.py (Recommended)
```bash
cd C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project
python manage.py migrate dtr 0004_add_dtr_history
```

### Method 2: Using the Custom Script
```bash
cd C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project
python run_dtr_migration.py
```

### Method 3: Run All Pending Migrations
```bash
cd C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project
python manage.py migrate
```

## Database Schema

### DTRHistory Table
```sql
CREATE TABLE dtr_dtrhistory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    date DATE NOT NULL,
    time_in TIME NOT NULL,
    time_out TIME NULL,
    selfie VARCHAR(100) NOT NULL,
    logout_selfie VARCHAR(100) NULL,
    hours_rendered FLOAT DEFAULT 0,
    notes TEXT,
    confirmation_status VARCHAR(20) NOT NULL,
    confirmed_by_id BIGINT NULL,
    confirmed_at DATETIME NULL,
    confirmation_remarks TEXT,
    original_created_at DATETIME NOT NULL,
    original_updated_at DATETIME NOT NULL,
    archived_at DATETIME NOT NULL,
    archived_reason VARCHAR(50) DEFAULT 'resubmission',
    
    FOREIGN KEY (student_id) REFERENCES accounts_user(id),
    FOREIGN KEY (confirmed_by_id) REFERENCES accounts_user(id),
    
    INDEX idx_student_date (student_id, date),
    INDEX idx_confirmation_status (confirmation_status)
);
```

## How It Works

### Workflow for Rejected DTR Resubmission:

1. **Supervisor Rejects DTR**
   - DTR status set to 'rejected'
   - Supervisor adds remarks explaining the rejection

2. **Student Views Rejected DTR**
   - Student sees "Resubmit" button on rejected DTR
   - Clicks to go to resubmit page

3. **Resubmission Page**
   - Shows rejection reason
   - Pre-fills form with current DTR data
   - Student can:
     - Edit time_in and time_out
     - Update notes
     - Capture new selfies (optional)

4. **Submission Process**
   - Old rejected DTR is archived to `DTRHistory`
   - New DTR created with status 'pending'
   - Old DTR is deleted from active records
   - Success message shown to student

5. **History View**
   - Student can view all archived DTRs
   - Full audit trail maintained
   - Shows who rejected, when, and why

## Integration Points

### In dtr_list.html (Current DTR List)
Add a link to view history:
```html
<a href="{% url 'student:dtr_history' %}" class="btn btn-secondary">
    <i class="bi bi-archive me-1"></i>View DTR History
</a>
```

### For Rejected DTRs (In table row)
Add resubmit button:
```html
{% if dtr.confirmation_status == 'rejected' %}
<a href="{% url 'student:dtr_resubmit' dtr.pk %}" class="btn btn-warning btn-sm">
    <i class="bi bi-arrow-clockwise me-1"></i>Resubmit
</a>
{% endif %}
```

## Testing Checklist

After migration:
- [ ] Check if DTRHistory table exists in database
- [ ] Test archiving a rejected DTR
- [ ] Test viewing DTR history
- [ ] Test resubmitting a rejected DTR
- [ ] Verify new DTR has 'pending' status
- [ ] Verify archived DTR appears in history
- [ ] Test pagination in history view
- [ ] Test detail modal in history view

## Troubleshooting

### Migration Errors
If migration fails:
```bash
# Check migration status
python manage.py showmigrations dtr

# Try running all migrations
python manage.py migrate

# If there's a conflict, try:
python manage.py migrate dtr --fake 0004_add_dtr_history
```

### Model Import Errors
If views can't import DTRHistory:
- Ensure migration has run successfully
- Restart Django development server
- Check that model is properly registered in `dtr/models.py`

## Summary

✅ **Migration File**: Created and ready
✅ **Models**: Already implemented
✅ **Views**: Already implemented
✅ **Templates**: Already created
✅ **URLs**: Already configured

**Next Step**: Run the migration command to create the database table!
