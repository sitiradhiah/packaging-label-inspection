@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dashboard_install
py -3.12 -c "import struct; assert struct.calcsize('P') == 8"
if errorlevel 1 goto python_missing
py -3.12 -m venv .venv
if errorlevel 1 goto fail
:dashboard_install
echo [1/3] Installing dashboard libraries...
".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 goto fail
if exist ".venv-train\Scripts\python.exe" goto ocr_check
py -3.12 -c "import struct; assert struct.calcsize('P') == 8"
if errorlevel 1 goto python_missing
py -3.12 -m venv .venv-train
if errorlevel 1 goto fail
:ocr_check
".venv-train\Scripts\python.exe" -c "import struct; assert struct.calcsize('P') == 8, 'OCR requires 64-bit Python'"
if errorlevel 1 goto fail
echo [2/3] Installing pretrained OCR libraries...
".venv-train\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements-ocr.txt
if errorlevel 1 goto fail
echo [3/3] Checking YOLO and OCR...
".venv\Scripts\python.exe" check_setup.py
if errorlevel 1 goto fail
echo Setup complete: YOLO and OCR passed. Open run.bat.
pause
exit /b 0
:python_missing
echo Install Python 3.12 64-bit with the Python launcher, then run setup.bat again.
pause
exit /b 1
:fail
echo Setup failed. Read the error above. Copy it when requesting help.
echo Check internet access, Python version and the downloaded model file.
pause
exit /b 1
