@echo off
REM Database setup script for TrendPulse (Windows)

echo Setting up TrendPulse Database...

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Generate migration
echo Generating initial migration...
alembic revision --autogenerate -m "initial_auth_tables"

echo.
echo Database setup complete!
echo.
echo Next steps:
echo 1. Review the generated migration in alembic/versions/
echo 2. Apply migration: alembic upgrade head
echo 3. Start the server: uvicorn app.main:app --reload

pause
