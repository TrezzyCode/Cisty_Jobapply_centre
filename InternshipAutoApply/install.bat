@echo off
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed. Check Python 3.10+ and your internet connection.
  pause
  exit /b 1
)
echo Dependencies installed.
pause
