@echo off
REM Communications App Startup Script for Windows

echo ========================================
echo Communications App Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    echo.
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Navigate to backend directory
cd backend

REM Start the server
echo Starting Communications App Server...
echo.
python server.py

REM Return to root directory
cd ..

pause
