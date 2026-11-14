@echo off
rem ============================================================
rem  Setup / upgrade Python dependencies into .\lib
rem  Requires Python 3.10+ on PATH.
rem  Usage:
rem    install.bat                  install (locked versions)
rem    install.bat --upgrade        upgrade packages
rem    install.bat --with-tesseract also download tesseract OCR
rem ============================================================
setlocal
set "BASE=%~dp0"
cd /d "%BASE%"

echo ============================================================
echo  Markdown Converter - setup
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ first:
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

python "%BASE%setup_deps.py" %*
echo.
pause
endlocal
