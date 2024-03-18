@echo off

@REM Admin privileges are needed because without them, the installer won't be able to place a shortcut to vRY in the Start Menu folder, therefore not allowing you to access vRY as easily.
@REM By "Start menu folder", I'm referring to C:\ProgramData\Microsoft\Windows\Start Menu\Programs
if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit /b)

cd %~dp0

vry.exe --install

PAUSE