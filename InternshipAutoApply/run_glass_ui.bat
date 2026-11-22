@echo off
setlocal
cd /d "%~dp0"

REM Resolve pythonw.exe from the selected Python installation. Running the UI
REM without a console prevents Windows QuickEdit/select mode from pausing Cisty.
for /f "usebackq delims=" %%P in (`py -3 -c "import sys; print(sys.executable)" 2^>nul`) do set "CISTY_PYTHON=%%P"
if not defined CISTY_PYTHON goto :missing
for %%P in ("%CISTY_PYTHON%") do set "CISTY_PYTHONW=%%~dpPpythonw.exe"
if not exist "%CISTY_PYTHONW%" goto :missing

start "" "%CISTY_PYTHONW%" "%~dp0qt_main.py"
exit /b 0

:missing
echo.
echo Cisty could not find pythonw.exe. Run install.bat first.
pause
exit /b 1
