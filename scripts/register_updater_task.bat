@echo off
setlocal

echo ============================================================
echo  VELOX Scheduled Update Task Manager
echo ============================================================

set TASK_NAME=VeloxUpdateCheck
set SCRIPT_PATH=%~dp0check_update.py

if "%1"=="--uninstall" goto uninstall
if "%1"=="-u" goto uninstall

:install
echo Registering daily background update check for VELOX...
schtasks /create /tn "%TASK_NAME%" /tr "python.exe \"%SCRIPT_PATH%\" --check-only" /sc daily /st 12:00 /f
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task "%TASK_NAME%" registered successfully.
    echo      Scheduled to run daily at 12:00 PM.
) else (
    echo [ERROR] Failed to register task. Please ensure you run this script as Administrator.
)
exit /b %ERRORLEVEL%

:uninstall
echo Removing scheduled update check task for VELOX...
schtasks /delete /tn "%TASK_NAME%" /f
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task "%TASK_NAME%" removed successfully.
) else (
    echo [INFO] Task was not found or already removed.
)
exit /b 0
