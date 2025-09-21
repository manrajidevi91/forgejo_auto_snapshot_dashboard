
@echo OFF
echo Uninstalling Forgejo Auto-Snapshot startup task...

set "TASK_NAME=ForgejoAutoSnapshotDashboard"

schtasks /delete /tn "%TASK_NAME%" /f

if %errorlevel% == 0 (
    echo Successfully removed startup task.
) else (
    echo Task not found or an error occurred.
)

pause
