@echo off
setlocal EnableDelayedExpansion

REM Define supported Python versions X.Y.Z for easy future updates
set SUPPORTED_MIN_VERSION=3.10
set SUPPORTED_MAX_VERSION=3.11.9

REM Extract for numeric comparison
for /f "tokens=1-3 delims=." %%a in ("%SUPPORTED_MIN_VERSION%") do (
    set /a MIN_MAJOR=%%a
    set /a MIN_MINOR=%%b
    set /a MIN_PATCH=%%c
)
for /f "tokens=1-3 delims=." %%a in ("%SUPPORTED_MAX_VERSION%") do (
    set /a MAX_MAJOR=%%a
    set /a MAX_MINOR=%%b
    set /a MAX_PATCH=%%c
)

if not defined MIN_PATCH set /a MIN_PATCH=0
if not defined MAX_PATCH set /a MAX_PATCH=0

REM Get Python version
for /f "tokens=2 delims= " %%I in ('python --version 2^>nul') do set PYTHON_VERSION=%%I

REM Check if Python is installed
if not defined PYTHON_VERSION (
    call :error "Python is not installed. Please install Python %SUPPORTED_MIN_VERSION% or %SUPPORTED_MAX_VERSION%."
    exit /b
)

REM Extract the version number
for /f "tokens=1-3 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

if not defined PATCH set PATCH=0

REM Convert to numeric
set /a MAJOR_NUM=!MAJOR!
set /a MINOR_NUM=!MINOR!
set /a PATCH_NUM=!PATCH!

REM Compare versions
call :compare_versions !MAJOR_NUM! !MINOR_NUM! !PATCH_NUM! %MIN_MAJOR% %MIN_MINOR% %MIN_PATCH% min_result
call :compare_versions !MAJOR_NUM! !MINOR_NUM! !PATCH_NUM! %MAX_MAJOR% %MAX_MINOR% %MAX_PATCH% max_result

if !min_result! lss 0 (
    call :error "Python version !PYTHON_VERSION! is lower than %SUPPORTED_MIN_VERSION%. Please install Python %SUPPORTED_MIN_VERSION% or %SUPPORTED_MAX_VERSION%."
    exit /b
)

if !max_result! gtr 0 (
    call :error "Python version !PYTHON_VERSION! is greater than %SUPPORTED_MAX_VERSION%. Please install Python %SUPPORTED_MIN_VERSION% or %SUPPORTED_MAX_VERSION%."
    exit /b
)

REM Install requirements
pip install -r requirements.txt
if %errorlevel% neq 0 (
    call :error "There was an error installing the requirements. Please check the output above for more details."
    exit /b
)

REM Success
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
exit /b

REM Compare two versions
:compare_versions
set /a v1=%1*10000 + %2*100 + %3
set /a v2=%4*10000 + %5*100 + %6
set /a %7=v1 - v2
goto :eof

REM Display error message
:error
echo.
echo.
echo.
echo.
echo.
echo.
echo %~1
echo.
echo.
echo.
echo Press any key to exit...
pause >nul
goto :eof
