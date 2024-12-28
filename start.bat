@echo off

REM Check if Python is installed using winget
winget list -e | findstr /i /C:"Python" >nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    winget install --id Python.Python -e
)

REM Set up a virtual environment if it doesn't exist
if not exist venv\Scripts\activate.bat (
    echo Setting up virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install requirements
python.exe -m pip install --upgrade pip beautifulsoup4 requests

python.exe -m pip list

REM Run the Python script
python scraper.py

REM Close the command prompt after the script finishes
pause
exit
