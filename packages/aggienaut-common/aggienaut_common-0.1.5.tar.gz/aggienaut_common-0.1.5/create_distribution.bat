@echo off
REM Distribution script for AggieNaut Common Package

echo Creating distribution package...

REM Create a distribution folder
if not exist "distribution" mkdir distribution
cd distribution

REM Copy the wheel file
copy "..\dist\aggienaut_common-0.1.0-py3-none-any.whl" .

REM Copy installation instructions
echo Creating installation instructions...
(
echo # AggieNaut Common Package Installation
echo.
echo ## Quick Install
echo ```bash
echo pip install aggienaut_common-0.1.0-py3-none-any.whl
echo ```
echo.
echo ## Verify Installation
echo ```python
echo import common
echo print^(f"AggieNaut Common v{common.__version__} installed successfully!"^)
echo ```
echo.
echo ## Dependencies
echo This package requires:
echo - Python ^>=3.8
echo - paho-mqtt^>=1.6.0
echo - pyserial^>=3.5
echo - toml^>=0.10.2
echo.
echo These will be installed automatically when you install the wheel.
) > INSTALL.md

echo Distribution package created in 'distribution' folder!
echo Contents:
dir /b
pause
