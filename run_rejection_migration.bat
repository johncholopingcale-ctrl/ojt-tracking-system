@echo off
REM Run DTR Rejection Enhancement Migration

echo ============================================================
echo DTR Rejection Enhancement Migration
echo ============================================================
echo.

cd /d "C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project"

echo Running migration to add is_valid field...
echo.
python manage.py migrate dtr 0005_add_is_valid_field

echo.
echo ============================================================
echo Migration Status:
echo ============================================================
python manage.py showmigrations dtr

echo.
echo ============================================================
echo Migration Complete!
echo ============================================================
echo.
echo New features added:
echo - is_valid field tracks DTR validity
echo - Rejected DTRs flagged as "Not Logged In"
echo - Student rejection reason modal
echo - Teacher rejected DTR list view
echo.
pause
