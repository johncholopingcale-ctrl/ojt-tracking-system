@echo off
REM Batch file to run DTR History migration

echo ============================================================
echo DTR History Migration Script
echo ============================================================
echo.

cd /d "C:\Users\pingc\OneDrive\Desktop\CODEERIST\ojt_project"

echo Current directory: %CD%
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo Virtual environment activated!
    echo.
) else if exist "..\venv\Scripts\activate.bat" (
    echo Activating virtual environment from parent directory...
    call ..\venv\Scripts\activate.bat
    echo Virtual environment activated!
    echo.
) else (
    echo Warning: Virtual environment not found. Using system Python...
    echo.
)

echo Running migration...
echo.
python manage.py migrate dtr 0004_add_dtr_history

echo.
echo ============================================================
echo Showing current migration status:
echo ============================================================
python manage.py showmigrations dtr

echo.
echo ============================================================
echo Migration process complete!
echo ============================================================
echo.
pause
