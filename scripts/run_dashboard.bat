
@echo OFF
REM Runs the Flask web dashboard.

echo Starting Forgejo Auto-Snapshot Dashboard...

REM Activate virtual environment if it exists
IF EXIST .\venv\Scripts\activate (
    echo Activating virtual environment...
    CALL .\venv\Scripts\activate
)

python main.py

pause
