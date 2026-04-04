@echo off
REM Install missing dependencies and run migration

echo ============================================================
echo Installing Missing Dependencies
echo ============================================================
echo.

cd /d "C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project"

echo Installing django-cloudinary-storage...
pip install django-cloudinary-storage

echo.
echo Installing all requirements from requirements.txt...
pip install -r requirements.txt

echo.
echo ============================================================
echo Dependencies installed! Now running migration...
echo ============================================================
echo.

python manage.py migrate dtr 0004_add_dtr_history

echo.
echo ============================================================
echo Showing migration status:
echo ============================================================
python manage.py showmigrations dtr

echo.
echo ============================================================
echo Done!
echo ============================================================
pause
