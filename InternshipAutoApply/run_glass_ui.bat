@echo off
cd /d "%~dp0"
py qt_main.py
if errorlevel 1 (
  echo.
  echo The new interface could not start. Run install.bat first.
  pause
)
