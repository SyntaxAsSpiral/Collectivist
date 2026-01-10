@echo off
REM Collectivist Collection Initializer (Windows)
REM Checks for Python + dependencies, installs what's needed and asks user if they want to begin analyzing

echo 🌸 Collectivist Collection Initializer
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not found
    echo    Please install Python 3.8+ from python.org and try again
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is required but not found
    echo    Please install pip and try again
    pause
    exit /b 1
)

echo ✅ Found pip
echo.

echo 📦 Checking dependencies...

REM Check for required packages and install if missing
set PACKAGES_TO_INSTALL=

python -c "import requests" >nul 2>&1
if errorlevel 1 set PACKAGES_TO_INSTALL=%PACKAGES_TO_INSTALL% requests

python -c "import yaml" >nul 2>&1
if errorlevel 1 set PACKAGES_TO_INSTALL=%PACKAGES_TO_INSTALL% pyyaml

python -c "import pathlib" >nul 2>&1
if errorlevel 1 set PACKAGES_TO_INSTALL=%PACKAGES_TO_INSTALL% pathlib

REM Install missing packages if any
if not "%PACKAGES_TO_INSTALL%"=="" (
    echo 📥 Installing missing packages:%PACKAGES_TO_INSTALL%
    python -m pip install%PACKAGES_TO_INSTALL%
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies satisfied
)

echo.
echo 🎯 Collection initialized successfully!
echo.

REM Ask if user wants to start analysis
set /p ANALYZE="Would you like to analyze this collection now? (y/N): "
if /i "%ANALYZE%"=="y" (
    echo 🔍 Starting collection analysis...
    python src\__main__.py analyze
) else (
    echo.
    echo 💡 To analyze later, run:
    echo    python .collection\src\__main__.py analyze
    echo.
    echo 📚 For help, run:
    echo    python .collection\src\__main__.py --help
)

pause