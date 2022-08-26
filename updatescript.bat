@echo off
robocopy %1 %2 /E /Move>NUL
rd /s /q %1>NUL
cd %2>NUL
@vRY.exe