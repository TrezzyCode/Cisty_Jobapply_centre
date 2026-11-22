@echo off
setlocal

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\Cisty"
set "TARGET_EXE=%INSTALL_DIR%\Cisty.exe"

tasklist /FI "IMAGENAME eq Cisty.exe" 2>nul | find /I "Cisty.exe" >nul
if not errorlevel 1 (
  echo Close Cisty before uninstalling it.
  pause
  exit /b 1
)

if exist "%TARGET_EXE%" del /F /Q "%TARGET_EXE%"
if exist "%INSTALL_DIR%" rmdir "%INSTALL_DIR%" 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "foreach($folder in @([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('Programs'))){$shortcut=Join-Path $folder 'Cisty.lnk'; if(Test-Path -LiteralPath $shortcut){Remove-Item -LiteralPath $shortcut -Force}}"

echo Cisty was uninstalled.
echo.
echo Your application history and settings were preserved in:
echo %LOCALAPPDATA%\IT Internship Auto Apply
echo.
echo Back up that folder before removing it manually.
pause
exit /b 0
