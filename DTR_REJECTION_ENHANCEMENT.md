# DTR Rejection Enhancement Implementation

## Overview
Enhanced the DTR rejection system to provide better visibility and tracking of rejected DTRs for both teachers and students.

## New Features

### 1. Invalid Time-In Flag
- **Field**: `is_valid` (Boolean) added to `DTRLog` model
- **Behavior**: Automatically set to `False` when DTR is rejected
- **Purpose**: Flags time-in as "Not Logged In" when rejected
- **Display**: Shows "Not Logged In" indicator on rejected DTRs

### 2. Student View Enhancements
- **Rejection Reason Button**: Added prominent button to view rejection reasons
- **Detailed Rejection Modal**: Pop-up showing:
  - Why the DTR was rejected
  - Who rejected it and when
  - Whether time-in is flagged as invalid
  - Quick resubmit option
- **Visual Indicators**: Clear status badges showing rejection and invalid status

### 3. Teacher View of Rejected DTRs
- **New Page**: `/teacher/dtr/rejected/`
- **Features**:
  - View all rejected DTRs across all students
  - See rejection reasons and supervisor comments
  - Check which DTRs are flagged as invalid
  - Filter by student or date
  - Pagination support

## Files Changed

### 1. Migration File
**File**: `dtr/migrations/0005_add_is_valid_field.py`
- Adds `is_valid` boolean field to DTRLog model
- Default value: `True`

### 2. Model Updates
**File**: `dtr/models.py`
- Added `is_valid` field (line ~136)
- Field tracks whether the DTR time-in is considered valid

### 3. View Updates
**File**: `evaluations/views.py` (DTRConfirmationView)
- **When confirming**: Sets `is_valid = True`
- **When rejecting**: Sets `is_valid = False` (flags as not logged in)
- Updated success/warning messages

**File**: `companies/views.py`
- Added `RejectedDTRListView` (lines ~263-298)
- Shows all rejected DTRs for teachers
- Includes statistics and filtering

### 4. URL Configuration
**File**: `companies/urls_teacher.py`
- Added route: `path('dtr/rejected/', views.RejectedDTRListView.as_view(), name='rejected_dtr_list')`

### 5. Template Updates

**File**: `templates/student/dtr_list.html`
- Added "Not Logged In" indicator for invalid DTRs
- Added red "View Rejection Reason" button
- Added detailed rejection reason modal with:
  - Rejection alert
  - Supervisor comments
  - DTR details summary
  - Quick resubmit action

**File**: `templates/teacher/rejected_dtr_list.html` (NEW)
- Complete interface for viewing rejected DTRs
- Table showing all rejected submissions
- Statistics badges (total rejected, students affected)
- Detailed modals for each rejection
- Shows validity status and supervisor remarks

## Database Schema Changes

```sql
-- New field added to dtr_dtrlog table
ALTER TABLE dtr_dtrlog ADD COLUMN is_valid BOOLEAN DEFAULT TRUE;
```

## How It Works

### Rejection Workflow:

1. **Supervisor Rejects DTR**
   - Sets `confirmation_status = 'rejected'`
   - Sets `is_valid = False` (flags time-in as invalid)
   - Adds `confirmation_remarks` (rejection reason)
   - Records `confirmed_by` and `confirmed_at`

2. **Student Views Rejection**
   - Sees "Rejected" badge with "Not Logged In" indicator
   - Clicks red "View Rejection Reason" button
   - Modal shows:
     - Who rejected and when
     - Supervisor's detailed comments
     - DTR details summary
     - Invalid flag notice
   - Can click "Resubmit Now" button

3. **Teacher Monitors Rejections**
   - Visits `/teacher/dtr/rejected/` page
   - Sees all rejected DTRs across students
   - Can view full details of each rejection
   - Monitors which DTRs are flagged as invalid
   - Tracks student compliance

4. **Student Resubmits**
   - Old rejected DTR archived to DTR History
   - New DTR created with `status = 'pending'` and `is_valid = True`
   - Awaits new supervisor review

## User Interface Examples

### Student DTR List View
```
Status Column:
┌─────────────────────┐
│ ❌ Rejected         │
│ ⚠️ Not Logged In   │  <- New indicator
└─────────────────────┘

Actions Column:
┌──────┬──────────┬──────────┐
│  👁️  │   ⚠️     │   🔄     │
│ View │ Reason   │ Resubmit │
└──────┴──────────┴──────────┘
        ^ New button
```

### Rejection Reason Modal (Student)
```
╔════════════════════════════════════════╗
║  ⚠️ DTR Rejected - March 30, 2026      ║
╠════════════════════════════════════════╣
║  ❌ This DTR was rejected              ║
║  ⚠️ Time-in flagged as NOT LOGGED IN   ║
║                                        ║
║  Rejected by: John Smith               ║
║  On: March 29, 2026 3:45 PM            ║
║                                        ║
║  💬 Supervisor's Comments:             ║
║  "Selfie photo is unclear. Please     ║
║   retake with better lighting."       ║
║                                        ║
║  📋 DTR Details                        ║
║  Date: Friday, March 30, 2026         ║
║  Time In: 8:00 AM                     ║
║  Time Out: 5:00 PM                    ║
║  Hours: 8.00 hours                    ║
║                                        ║
║  💡 What to do next:                   ║
║  You can resubmit this DTR with       ║
║  corrections by clicking Resubmit.    ║
║                                        ║
║  [ Close ]  [ 🔄 Resubmit Now ]       ║
╚════════════════════════════════════════╝
```

### Teacher Rejected DTR List
```
┌──────────────────────────────────────────────────────────────┐
│  ❌ Rejected DTR Logs                                         │
│                                                               │
│  [5 Rejected DTRs]  [3 Students Affected]                   │
├──────────────────────────────────────────────────────────────┤
│ Student    │ Date       │ Valid Status  │ Rejected By       │
├────────────┼────────────┼───────────────┼───────────────────┤
│ Jane Doe   │ Mar 30, 26 │ ❌ Invalid    │ John Smith        │
│            │            │ Not logged in │ Mar 29, 3:45 PM   │
│            │            │               │ [View Reason]     │
├────────────┼────────────┼───────────────┼───────────────────┤
│ ...        │            │               │                   │
└──────────────────────────────────────────────────────────────┘
```

## Testing Checklist

After running migrations:

- [ ] Run migration: `python manage.py migrate dtr 0005_add_is_valid_field`
- [ ] Test supervisor rejection (should set is_valid=False)
- [ ] Verify "Not Logged In" indicator appears on student view
- [ ] Test "View Rejection Reason" button and modal
- [ ] Access teacher rejected DTR list: `/teacher/dtr/rejected/`
- [ ] Verify rejection reasons display correctly
- [ ] Test DTR resubmission (should reset is_valid=True)
- [ ] Check that confirmed DTRs have is_valid=True
- [ ] Verify pagination works on rejected DTR list
- [ ] Test modal details on teacher rejected DTR list

## Migration Commands

### Run the new migration:
```bash
cd C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project
python manage.py migrate dtr 0005_add_is_valid_field
```

### Check migration status:
```bash
python manage.py showmigrations dtr
```

Expected output:
```
dtr
 [X] 0001_initial
 [X] 0002_...
 [X] 0003_dtrlog_logout_selfie
 [X] 0004_add_dtr_history
 [X] 0005_add_is_valid_field
```

## API/URL Endpoints

### New URLs:
- **Teacher Rejected DTRs**: `/teacher/dtr/rejected/`
  - View: `RejectedDTRListView`
  - Template: `teacher/rejected_dtr_list.html`
  - Permission: Teacher role required

### Updated Behavior:
- **DTR Confirmation**: `/supervisor/dtr/<id>/confirm/`
  - Now sets `is_valid` field when confirming/rejecting

## Summary of Changes

| Component | Change | Purpose |
|-----------|--------|---------|
| DTRLog Model | Added `is_valid` field | Track if time-in is valid |
| DTR Confirmation | Set is_valid=False on reject | Flag invalid time-ins |
| Student Template | Added rejection modal & button | Better rejection visibility |
| Teacher View | New rejected DTR list page | Monitor all rejections |
| Database | New boolean column | Store validity status |

## Benefits

1. **Better Transparency**: Students can easily see why their DTR was rejected
2. **Teacher Oversight**: Teachers can monitor all rejections across students
3. **Invalid Flag**: Clear indication when time-in is not considered valid
4. **Audit Trail**: Complete history of rejections and reasons
5. **Quick Action**: Students can quickly resubmit from rejection modal
6. **Compliance Tracking**: Teachers can identify patterns in rejections

## Next Steps

1. Run the migration
2. Test the rejection workflow
3. Train supervisors on providing clear rejection reasons
4. Monitor the rejected DTR list for patterns
5. Consider adding email notifications for rejections (future enhancement)
