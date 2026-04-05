@echo off
cd /d "C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project"
echo ============================================================
echo Running Django Migrations
echo ============================================================
echo.
echo Step 1: Creating migration...
python manage.py makemigrations dtr --name add_login_logout_confirmation
echo.
if %errorlevel% equ 0 (
    echo Step 2: Applying migration...
    python manage.py migrate
) else (
    echo Migration creation failed!
)
echo.
echo Done!
