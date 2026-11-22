@echo off
setlocal
cd /d "%~dp0"

set "SOURCE_EXE=%CD%\Cisty.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\Cisty"
set "TARGET_EXE=%INSTALL_DIR%\Cisty.exe"

echo Cisty installer
echo.

if not exist "%SOURCE_EXE%" (
  echo ERROR: Cisty.exe was not found in this folder.
  echo Ask the distributor for a complete UserPack.
  pause
  exit /b 1
)

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if errorlevel 1 (
  echo ERROR: The installation folder could not be created.
  pause
  exit /b 1
)

copy /Y "%SOURCE_EXE%" "%TARGET_EXE%" >nul
if errorlevel 1 (
  echo ERROR: The EXE could not be copied. Close the application and try again.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$target=Join-Path $env:LOCALAPPDATA 'Programs\Cisty\Cisty.exe'; $shell=New-Object -ComObject WScript.Shell; foreach($folder in @([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('Programs'))){$shortcut=$shell.CreateShortcut((Join-Path $folder 'Cisty.lnk')); $shortcut.TargetPath=$target; $shortcut.WorkingDirectory=(Split-Path $target); $shortcut.Description='Cisty'; $shortcut.Save()}"
if errorlevel 1 (
  echo WARNING: The application was installed, but shortcuts could not be created.
  echo You can run it from: "%TARGET_EXE%"
  pause
  exit /b 0
)

echo.
echo Installation complete.
echo Your private application data is stored separately in LOCALAPPDATA.
start "" "%TARGET_EXE%"
exit /b 0
