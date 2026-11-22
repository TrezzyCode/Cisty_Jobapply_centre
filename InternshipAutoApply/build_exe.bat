@echo off
cd /d "%~dp0"
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --windowed --name IT_Internship_Auto_Apply main.py
if errorlevel 1 (
  echo EXE build failed.
  pause
  exit /b 1
)
echo EXE created in dist\IT_Internship_Auto_Apply\
pause
