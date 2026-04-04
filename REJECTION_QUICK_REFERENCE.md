# DTR Rejection Enhancement - Quick Reference

## 🚀 Quick Start

### 1. Run Migration
```bash
cd C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project
python manage.py migrate dtr 0005_add_is_valid_field
```

Or use the batch file:
```bash
.\run_rejection_migration.bat
```

### 2. Push to Git
```bash
.\git_push_rejection_enhancement.bat
```

---

## ✨ New Features

### For Students:
1. **Rejection Reason Button** - Red button to view why DTR was rejected
2. **Detailed Modal** - Shows supervisor comments and rejection details
3. **Invalid Flag** - "Not Logged In" indicator for rejected DTRs
4. **Quick Resubmit** - Direct link to resubmit from rejection modal

### For Teachers:
1. **Rejected DTR List** - `/teacher/dtr/rejected/` page
2. **View All Rejections** - See rejected DTRs from all students
3. **Statistics** - Count of rejected DTRs and affected students
4. **Supervisor Comments** - View rejection reasons and supervisor remarks

### For Supervisors:
1. **Auto-Flagging** - Rejected DTRs automatically flagged as invalid
2. **Clear Messaging** - Students notified they can resubmit

---

## 📋 Files Modified

| File | What Changed |
|------|--------------|
| `dtr/models.py` | Added `is_valid` field |
| `dtr/migrations/0005_add_is_valid_field.py` | Migration for new field |
| `evaluations/views.py` | Set is_valid on reject/confirm |
| `companies/views.py` | Added RejectedDTRListView |
| `companies/urls_teacher.py` | Added rejected DTR route |
| `templates/student/dtr_list.html` | Added rejection modal |
| `templates/teacher/rejected_dtr_list.html` | New teacher view |

---

## 🔍 How to Test

### Test Rejection Flow:
1. As **Supervisor**: Reject a student DTR with comments
2. As **Student**: 
   - See "Rejected" + "Not Logged In" status
   - Click red button to view rejection reason
   - Read supervisor comments in modal
   - Click "Resubmit Now"
3. As **Teacher**:
   - Visit `/teacher/dtr/rejected/`
   - See the rejected DTR in list
   - Click "View Reason" to see details

### Test Confirmation Flow:
1. As **Supervisor**: Confirm a DTR
2. Verify `is_valid` is set to `True`
3. Verify student sees "Confirmed" status

---

## 🎯 Key Behaviors

### When DTR is Rejected:
```python
confirmation_status = 'rejected'
is_valid = False  # ← Time-in flagged as invalid
confirmed_by = supervisor
confirmed_at = now
confirmation_remarks = "reason..."
```

### When DTR is Confirmed:
```python
confirmation_status = 'confirmed'
is_valid = True  # ← Time-in is valid
confirmed_by = supervisor
confirmed_at = now
```

### When DTR is Resubmitted:
```python
# Old DTR archived to DTRHistory
# New DTR created:
confirmation_status = 'pending'
is_valid = True  # ← Reset to valid
```

---

## 📊 Database Schema

```sql
-- New column in dtr_dtrlog table
is_valid BOOLEAN DEFAULT TRUE

-- When rejected:
UPDATE dtr_dtrlog 
SET is_valid = FALSE, 
    confirmation_status = 'rejected'
WHERE id = <rejected_dtr_id>;
```

---

## 🔗 URL Routes

| Role | URL | Description |
|------|-----|-------------|
| Student | `/student/dtr/` | View own DTRs with rejection buttons |
| Student | Modal in page | View rejection reason |
| Teacher | `/teacher/dtr/rejected/` | View all rejected DTRs |
| Supervisor | `/supervisor/dtr/<id>/confirm/` | Confirm/reject DTR |

---

## 💡 Tips

1. **Supervisors** should provide clear, actionable rejection reasons
2. **Students** can see complete rejection history in DTR History page
3. **Teachers** can monitor trends in rejections via the new page
4. Rejected DTRs remain in active list until resubmitted (then archived)
5. The `is_valid` flag helps identify which time-ins don't count toward hours

---

## 🐛 Troubleshooting

### Migration fails?
```bash
# Check current migrations
python manage.py showmigrations dtr

# Run all pending migrations
python manage.py migrate
```

### is_valid not showing?
```bash
# Run the migration again
python manage.py migrate dtr 0005_add_is_valid_field

# Check if field exists in database
python manage.py dbshell
# Then: \d dtr_dtrlog  (PostgreSQL) or DESCRIBE dtr_dtrlog; (MySQL)
```

### Template not found?
- Verify `templates/teacher/rejected_dtr_list.html` exists
- Restart Django development server
- Check URL: `/teacher/dtr/rejected/`

---

## 📈 Success Metrics

After implementation, you should see:
- ✅ Rejected DTRs clearly marked as "Not Logged In"
- ✅ Students can easily view rejection reasons
- ✅ Teachers have visibility into all rejections
- ✅ Clear audit trail of why DTRs were rejected
- ✅ Reduced confusion about DTR status

---

## 🔄 Workflow Summary

```
Student logs DTR
       ↓
Supervisor reviews
       ↓
    Rejected? ─── No ──→ Confirmed (is_valid=True)
       ↓ Yes
Set is_valid=False
Add rejection remarks
       ↓
Student sees:
- Rejected status
- Not Logged In flag
- View Reason button
       ↓
Student clicks View Reason
Sees supervisor comments
       ↓
Student clicks Resubmit
Old DTR → History
New DTR created (is_valid=True)
       ↓
Back to Supervisor review
```

---

## 📞 Need Help?

See full documentation: `DTR_REJECTION_ENHANCEMENT.md`
