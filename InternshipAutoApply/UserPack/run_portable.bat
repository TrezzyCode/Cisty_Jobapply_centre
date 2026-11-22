@echo off
setlocal
cd /d "%~dp0"

if not exist "Cisty.exe" (
  echo ERROR: Cisty.exe was not found in this folder.
  pause
  exit /b 1
)

start "" "%CD%\Cisty.exe"
exit /b 0
