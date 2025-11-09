@echo off
echo ========================================
echo Installing Tesseract OCR for Windows
echo ========================================
echo.

REM Check if Chocolatey is installed
where choco >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Chocolatey found! Installing Tesseract...
    choco install tesseract -y
    goto :end
)

REM Check if winget is available
where winget >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Winget found! Installing Tesseract...
    winget install --id UB-Mannheim.TesseractOCR
    goto :end
)

REM Manual installation instructions
echo ========================================
echo Please install Tesseract OCR manually:
echo ========================================
echo.
echo 1. Download installer from:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. Run the installer (tesseract-ocr-w64-setup-*.exe)
echo.
echo 3. During installation, note the installation path
echo    (usually: C:\Program Files\Tesseract-OCR)
echo.
echo 4. After installation, run this script again to configure
echo.
echo Opening download page in browser...
start https://github.com/UB-Mannheim/tesseract/wiki
pause

:end
echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Tesseract should now be available.
echo.
pause
