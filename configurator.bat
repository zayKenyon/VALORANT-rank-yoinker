@echo off
"vRY.exe" --config 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo Executable failed, trying Python...
    python main.py --config 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Python also failed!
        echo Try reinstalling VRY or Python to fix this issue.
        pause >nul
    )
)
