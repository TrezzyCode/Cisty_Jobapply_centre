@echo off
setlocal
cd /d "%~dp0"

echo [1/5] Checking Python...
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher was not found. Install Python 3.10 or newer first.
  pause
  exit /b 1
)
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)

echo [2/5] Installing build dependencies...
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :failed
py -3 -m pip install "pyinstaller>=6.10" "Pillow>=10.3"
if errorlevel 1 goto :failed

echo [3/5] Generating Cisty icon assets...
py -3 tools\generate_brand_assets.py
if errorlevel 1 goto :failed

echo [4/5] Building the current PySide6 interface...
REM Only source code and the starter workbook are bundled. Personal settings,
REM databases, resumes, OAuth credentials, Gmail tokens, and avatars remain in
REM each user's LOCALAPPDATA folder and are never included in the EXE.
py -3 -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name Cisty ^
  --icon "assets\cisty_app_icon.ico" ^
  --add-data "assets;assets" ^
  --add-data "CareeReX_IT_highlight.xlsx;." ^
  qt_main.py
if errorlevel 1 goto :failed

echo [5/5] Build complete.
echo EXE: %CD%\dist\Cisty.exe
echo Test this EXE on a clean Windows account before sharing it.
pause
exit /b 0

:failed
echo EXE build failed. Review the messages above.
pause
exit /b 1
