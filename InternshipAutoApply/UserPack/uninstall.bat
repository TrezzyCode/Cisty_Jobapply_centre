@echo off
setlocal

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\Internship Workspace"
set "TARGET_EXE=%INSTALL_DIR%\InternshipWorkspace.exe"

tasklist /FI "IMAGENAME eq InternshipWorkspace.exe" 2>nul | find /I "InternshipWorkspace.exe" >nul
if not errorlevel 1 (
  echo Close Internship Workspace before uninstalling it.
  pause
  exit /b 1
)

if exist "%TARGET_EXE%" del /F /Q "%TARGET_EXE%"
if exist "%INSTALL_DIR%" rmdir "%INSTALL_DIR%" 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "foreach($folder in @([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('Programs'))){$shortcut=Join-Path $folder 'Internship Workspace.lnk'; if(Test-Path -LiteralPath $shortcut){Remove-Item -LiteralPath $shortcut -Force}}"

echo Internship Workspace was uninstalled.
echo.
echo Your application history and settings were preserved in:
echo %LOCALAPPDATA%\IT Internship Auto Apply
echo.
echo Back up that folder before removing it manually.
pause
exit /b 0
