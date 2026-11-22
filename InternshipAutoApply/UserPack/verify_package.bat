@echo off
setlocal
cd /d "%~dp0"
set "FAILED=0"

call :check "Cisty.exe"
call :check "install.bat"
call :check "run_portable.bat"
call :check "uninstall.bat"
call :check "README_FIRST.md"
call :check "docs\01_GMAIL_SETUP.md"
call :check "docs\02_GEOAPIFY_SETUP.md"
call :check "docs\03_SOFTWARE_GUIDE.md"
call :check "docs\04_PRIVACY_AND_SAFETY.md"
call :check "docs\05_TROUBLESHOOTING.md"

echo.
if "%FAILED%"=="0" (
  echo UserPack check passed.
) else (
  echo UserPack is incomplete. Add the missing files before sharing it.
)
pause
exit /b %FAILED%

:check
if exist "%~1" (
  echo [OK]      %~1
) else (
  echo [MISSING] %~1
  set "FAILED=1"
)
exit /b 0
