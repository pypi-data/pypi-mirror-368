@echo off
REM Installation script for AggieNaut Common Package

echo Installing AggieNaut Common Package...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install the wheel
if exist "dist\aggienaut_common-0.1.0-py3-none-any.whl" (
    echo Installing from wheel...
    pip install "dist\aggienaut_common-0.1.0-py3-none-any.whl"
) else (
    echo Wheel file not found. Installing from source...
    pip install .
)

if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b 1
) else (
    echo Installation successful!
    python -c "import common; print(f'AggieNaut Common v{common.__version__} installed successfully!')"
)

pause
