@echo off
setlocal
cd /d "%~dp0"

if not exist "InternshipWorkspace.exe" (
  echo ERROR: InternshipWorkspace.exe was not found in this folder.
  pause
  exit /b 1
)

start "" "%CD%\InternshipWorkspace.exe"
exit /b 0
