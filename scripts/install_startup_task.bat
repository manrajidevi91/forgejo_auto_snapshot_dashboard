@echo OFF
echo Registering Forgejo Auto-Snapshot Dashboard to run on startup...

REM Get the full path to the run_dashboard.bat script
set "SCRIPT_PATH=%~dp0run_dashboard.bat"

REM Define the task name
set "TASK_NAME=ForgejoAutoSnapshotDashboard"

REM Check if task already exists and delete it
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% == 0 (
    echo Task already exists. Deleting it first...
    schtasks /delete /tn "%TASK_NAME%" /f
)

REM Create the startup task
echo Creating new startup task...
schtasks /create /tn "%TASK_NAME%" /tr "%SCRIPT_PATH%" /sc ONLOGON /rl HIGHEST /f

if %errorlevel% == 0 (
    echo Successfully created startup task!
) else (
    echo Failed to create startup task. Please run this script as an administrator.
)

pause
