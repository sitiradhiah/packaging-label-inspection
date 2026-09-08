@echo off
cd /d "%~dp0"
py -m venv .venv
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Setup complete. Open run.bat to start.
pause
exit /b 0
:fail
echo Setup failed. Check Python installation and internet connection.
pause
exit /b 1

