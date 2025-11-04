@echo off
echo ========================================
echo Google Calendar OAuth Setup
echo ========================================
echo.
echo This script will:
echo   1. Install required package (google-auth-oauthlib)
echo   2. Generate a new OAuth token with Calendar access
echo   3. Update your .env file
echo.
echo ========================================
pause

cd backend

echo.
echo [1/3] Installing google-auth-oauthlib...
echo ========================================
.venv\Scripts\pip.exe install google-auth-oauthlib
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)

echo.
echo [2/3] Enabling Google Calendar API...
echo ========================================
echo IMPORTANT: Before continuing, make sure you have:
echo.
echo   1. Go to: https://console.cloud.google.com/apis/library
echo   2. Search for "Google Calendar API"
echo   3. Click ENABLE
echo.
echo ========================================
echo Press any key when you've enabled Calendar API...
pause

echo.
echo [3/3] Generating OAuth Token...
echo ========================================
echo Your browser will open automatically.
echo Please sign in and authorize BOTH Gmail and Calendar access.
echo.
.venv\Scripts\python.exe get_calendar_token.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: OAuth token generation failed
    echo See CALENDAR_OAUTH_SETUP.md for troubleshooting
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Calendar OAuth setup complete
echo ========================================
echo.
echo Next step: Update your .env file with the new refresh token printed above
echo.
echo Then restart your server:
echo   cd backend
echo   .venv\Scripts\python.exe -u server.py
echo.
pause
