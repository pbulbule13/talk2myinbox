@echo off
echo Starting Cognitive Journal Agent API Server...
echo.
echo The web UI will be available at:
echo http://localhost:7000
echo.
echo API documentation at:
echo http://localhost:7000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
python main.py api
pause
