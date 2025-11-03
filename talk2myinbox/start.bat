@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Talk2MyInbox - Application Starter
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if uv is installed
echo [1/6] Checking UV installation...
uv --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: UV is not installed!
    echo Please install UV from: https://github.com/astral-sh/uv
    echo Or run: pip install uv
    pause
    exit /b 1
)
echo ✓ UV is installed

REM Navigate to backend directory
cd backend
if %ERRORLEVEL% neq 0 (
    echo ERROR: Backend directory not found!
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create it
echo.
echo [2/6] Setting up virtual environment...
if not exist ".venv" (
    echo Creating new virtual environment with UV...
    uv venv
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Install/update dependencies
echo.
echo [3/6] Installing dependencies...
uv pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    echo Trying alternative method...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo ERROR: All installation methods failed!
        pause
        exit /b 1
    )
)
echo ✓ Dependencies installed

REM Check if .env file exists
echo.
echo [4/6] Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
        echo ✓ .env file created from example
    ) else (
        echo NOTE: No .env file found - application will run in MOCK mode
        echo   This is normal for first-time setup
        echo   Real Gmail/Calendar integration requires API credentials
    )
) else (
    echo ✓ Configuration file exists
)

REM Kill any existing Python processes on port 8000
echo.
echo [5/6] Checking for existing server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing existing process on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)
echo ✓ Port 8000 is available

REM Start the server
echo.
echo [6/6] Starting Talk2MyInbox server...
echo.
echo ========================================
echo  Server Information
echo ========================================
echo  URL: http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Status: Starting...
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server using uv run
.venv\Scripts\python.exe server.py

REM If server stops, show message
echo.
echo ========================================
echo  Server Stopped
echo ========================================
echo.
pause
