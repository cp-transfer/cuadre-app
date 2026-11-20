@echo off
setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo        CUADRE APP - WINDOWS SETUP
echo ========================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python Launcher (py) was not found.
    echo Install Python 3.12 or newer first.
    exit /b 1
)

py -3 -c "import sys; assert sys.version_info.major*100+sys.version_info.minor>=312"
if errorlevel 1 (
    echo ERROR: Python 3.12 or newer is required.
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo ERROR: Could not create the virtual environment.
        exit /b 1
    )
)

set "PYTHON=.venv\Scripts\python.exe"

"%PYTHON%" -c "import sys; assert sys.version_info.major*100+sys.version_info.minor>=312"
if errorlevel 1 (
    echo ERROR: The existing virtual environment is invalid or uses Python older than 3.12.
    echo Delete the .venv folder and run this installer again.
    exit /b 1
)

echo.
echo Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo.
if /i "%~1"=="dev" (
    echo Installing Cuadre App with development dependencies...
    "%PYTHON%" -m pip install ".[dev]"
) else (
    echo Installing Cuadre App...
    "%PYTHON%" -m pip install .
)
if errorlevel 1 exit /b 1

echo.
echo ========================================
echo Installation completed successfully.
echo ========================================
echo.
echo Launch with:
echo .venv\Scripts\python.exe -m cuadre
echo.

endlocal
