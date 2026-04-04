@echo off
REM Git Push Script for DTR Rejection Enhancement

echo ============================================================
echo Git Push - DTR Rejection Enhancement
echo ============================================================
echo.

cd /d "C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project"

echo Step 1: Adding files...
echo.

git add dtr/migrations/0005_add_is_valid_field.py
git add dtr/models.py
git add evaluations/views.py
git add companies/views.py
git add companies/urls_teacher.py
git add templates/student/dtr_list.html
git add templates/teacher/rejected_dtr_list.html

echo.
echo Step 2: Git status...
echo.
git status

echo.
echo Step 3: Creating commit...
echo.

git commit -m "Enhance DTR rejection system with validity tracking" -m "Features:" -m "- Add is_valid field to track DTR validity status" -m "- Flag rejected DTRs as 'Not Logged In'" -m "- Add rejection reason modal for students" -m "- Create teacher view for all rejected DTRs" -m "- Show supervisor comments and rejection details" -m "- Display invalid status indicators" -m "" -m "Changes:" -m "- Migration: Add is_valid boolean field to DTRLog" -m "- Model: Added is_valid field (default=True)" -m "- View: Auto-set is_valid=False on rejection" -m "- Student UI: Rejection reason button and detailed modal" -m "- Teacher UI: New rejected DTR list page with statistics" -m "- URLs: Added /teacher/dtr/rejected/ route" -m "" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo.
echo Step 4: Pushing to remote...
echo.
git push

echo.
echo ============================================================
echo Done! All changes pushed successfully!
echo ============================================================
echo.
echo Files committed:
echo - dtr/migrations/0005_add_is_valid_field.py
echo - dtr/models.py
echo - evaluations/views.py
echo - companies/views.py
echo - companies/urls_teacher.py
echo - templates/student/dtr_list.html
echo - templates/teacher/rejected_dtr_list.html
echo.
pause
