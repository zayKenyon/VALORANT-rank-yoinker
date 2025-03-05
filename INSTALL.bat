@echo off

REM Get Python version using python command
for /f "tokens=2 delims= " %%I in ('python --version 2^>nul') do set PYTHON_VERSION=%%I

REM Check if Python is installed
if not defined PYTHON_VERSION (
    echo.
    echo.
    echo.
    echo.
    echo.
    echo.
    echo Python is not installed. Please install Python and try again.
    echo.
    echo.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
)

REM Extract the version number
for /f "tokens=1-3 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

REM Check if Python version is < 3.10
if %MAJOR% lss 3 (
    echo.
    echo.
    echo.
    echo.
    echo.
    echo.
    echo Python version is lower than 3.10. Please install Python 3.10 or 3.11 or 3.12.
    echo.
    echo.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
)

if %MAJOR%==3 if %MINOR% lss 10 (
    echo.
    echo.
    echo.
    echo.
    echo.
    echo.
    echo Python version is lower than 3.10. Please install Python 3.10 or 3.11 or 3.12.
    echo.
    echo.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
)

REM Check if Python version is > 3.12
if %MAJOR% gtr 3 (
    if %MINOR% gtr 12 (
        echo.
        echo.
        echo.
        echo.
        echo.
        echo.
        echo Python version is greater than 3.12. Please install Python 3.10 or 3.11 or 3.12.
        echo.
        echo.
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b
    )
)

if %MAJOR%==3 if %MINOR% gtr 12 (
    echo.
    echo.
    echo.
    echo.
    echo.
    echo.
    echo Python version is greater than 3.12. Please install Python 3.10 or 3.11 or 3.12.
    echo.
    echo.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
)

REM Install requirements from requirements.txt
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo.
    echo.
    echo.
    echo There was an error installing the requirements. Please check the output above for more details.
    echo.
    echo.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
)

REM Success message
echo.
echo.
echo.
echo.
echo.
echo.
echo Requirements were successfully installed.
echo Use START.bat to start.
echo.
echo.
echo.
echo Press any key to exit...
pause >nul
