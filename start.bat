@echo off
SETLOCAL

REM ===== Check if Python is installed =====
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.13+ and try again.
    pause
    exit /b
)

REM ===== Create venv if not exists =====
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM ===== Activate venv =====
call venv\Scripts\activate.bat

REM ===== Install requirements =====
echo Installing required packages...

REM Check/install psutil
python -c "import psutil; print('Requirement already satisfied: psutil')" 2>nul || pip install psutil
REM Check/install rich
python -c "import rich; print('Requirement already satisfied: rich')" 2>nul || pip install rich

REM ===== Run Cherubin =====
echo Launching Cherubin...
python cherubin.py %*

REM ===== Deactivate venv =====
call venv\Scripts\deactivate.bat

ENDLOCAL
pause
