@echo off

echo SCRIPT MADE BY SECONB (WITH CHATGPT), INSTALLING EVERYTHING YOU NEED AUTOMATICALLY

:: Ensure the script runs in the same directory where it is saved
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python and check "Add Python.EXE to PATH".
    pause
    exit /b
)

:: Upgrade pip to ensure smooth installations
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install required libraries
set LIBRARIES=Pillow pywin32 bettercam configparser opencv-python numpy colorama pyserial

for %%L in (%LIBRARIES%) do (
    echo Installing %%L...
    python -m pip install %%L
    if errorlevel 1 (
        echo Failed to install %%L. Please check for errors.
    )
)

echo All installations completed.
pause