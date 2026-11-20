
@echo off
setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo        CUADRE APP - WINDOWS SETUP
echo ========================================
echo.

where.exe py >nul 2>&1
if errorlevel 1 goto no_launcher

py -3 -c "import sys; assert sys.version_info.major*100+sys.version_info.minor>=312"
if errorlevel 1 goto old_python

if exist ".venv\Scripts\python.exe" goto validate_venv

echo Creating virtual environment...
py -3 -m venv .venv
if errorlevel 1 goto venv_failed

:validate_venv
set "PYTHON=%CD%\.venv\Scripts\python.exe"

if not exist "%PYTHON%" goto venv_failed

"%PYTHON%" -c "import sys; assert sys.version_info.major*100+sys.version_info.minor>=312"
if errorlevel 1 goto invalid_venv

echo.
echo Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto pip_failed

echo.
if /i "%~1"=="dev" goto install_dev

echo Installing Cuadre App...
"%PYTHON%" -m pip install .
if errorlevel 1 goto install_failed
goto success

:install_dev
echo Installing Cuadre App with development dependencies...
"%PYTHON%" -m pip install ".[dev]"
if errorlevel 1 goto install_failed
goto success

:success
echo.
echo ========================================
echo Installation completed successfully.
echo ========================================
echo.
echo Launch with:
echo .venv\Scripts\python.exe -m cuadre
echo.
endlocal
exit /b 0

:no_launcher
echo ERROR: Python Launcher py was not found.
echo Install Python 3.12 or newer first.
goto failed

:old_python
echo ERROR: Python 3.12 or newer is required.
goto failed

:venv_failed
echo ERROR: Could not create the virtual environment.
goto failed

:invalid_venv
echo ERROR: Existing virtual environment is invalid or uses Python older than 3.12.
echo Delete the .venv folder and run this installer again.
goto failed

:pip_failed
echo ERROR: Could not upgrade pip.
goto failed

:install_failed
echo ERROR: Could not install Cuadre App.
goto failed

:failed
echo.
echo Installation failed.
endlocal
exit /b 1
