@echo off
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Dex Researcher starting...
echo Open http://localhost:8000 in your browser.
echo.

python main.py
if errorlevel 1 (
    echo.
    echo Server exited with an error. Check the message above.
    pause
)
