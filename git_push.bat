@echo off
REM Git Push Script for DTR History Feature

echo ============================================================
echo Git Push Script - DTR History Feature
echo ============================================================
echo.

cd /d "C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project"

echo Current directory: %CD%
echo.

echo ============================================================
echo Step 1: Checking Git Status
echo ============================================================
git status
echo.

echo ============================================================
echo Step 2: Adding Untracked Files
echo ============================================================
echo Adding migration file...
git add dtr/migrations/0004_add_dtr_history.py

echo Adding DTR history template...
git add templates/student/dtr_history.html

echo Adding DTR resubmit template...
git add templates/student/dtr_resubmit.html

echo.
echo Files added successfully!
echo.

echo ============================================================
echo Step 3: Showing What Will Be Committed
echo ============================================================
git status
echo.

echo ============================================================
echo Step 4: Creating Commit
echo ============================================================
git commit -m "Add DTR history and resubmission feature" -m "- Add DTRHistory model to track archived and rejected DTR submissions" -m "- Add DTR history view for students to view archived logs" -m "- Add DTR resubmit functionality for rejected DTRs" -m "- Archive rejected DTRs when student resubmits" -m "- Add pagination and detail modals for history view" -m "- Integrate history and resubmit links in DTR list" -m "" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo.
echo Commit created successfully!
echo.

echo ============================================================
echo Step 5: Pushing to Remote Repository
echo ============================================================
git push

echo.
echo ============================================================
echo Done! Changes pushed successfully!
echo ============================================================
echo.

echo Summary of changes:
echo - Added DTR history migration (0004_add_dtr_history.py)
echo - Added DTR history template (dtr_history.html)
echo - Added DTR resubmit template (dtr_resubmit.html)
echo.

pause
