# Internship Workspace

## Run the approved glass interface

1. Install Python 3.10 or newer.
2. Run `install.bat` once. This installs PySide6 and the existing Excel/Gmail dependencies.
3. Run `run_glass_ui.bat`.

The new interface reads the same local database and settings as the existing application. It does not create a second company list or expose unrelated Gmail messages.

## Existing interface

`run.bat` still starts the previous Tkinter interface. Keep it as a fallback while the new Qt interface is being tested.

## Local data

Each Windows user has separate data under:

`%LOCALAPPDATA%\IT Internship Auto Apply`

This includes application history, settings, the database, Gmail authorization token, and the optional profile photo selected in My Workspace. The sidebar falls back to the user's initials when no photo is selected. Do not copy that folder when sharing the application with another person.

## Packaging

The current PySide6 interface has not been packaged as an EXE yet. After it is tested on the target Windows resolutions, run `build_exe.bat`. The script creates `dist\InternshipWorkspace.exe` and deliberately excludes local settings, databases, Gmail tokens, resumes, credentials, and profile photos.

After building, copy `dist\InternshipWorkspace.exe` into `UserPack\`. The UserPack contains a no-admin installer, portable launcher, uninstaller, package checker, Gmail/Geoapify setup instructions, user guide, privacy notes, and troubleshooting guide. EXE and ZIP files inside UserPack are intentionally excluded from Git.

## Project handoff

See `HANDOFF.md` for architecture, privacy boundaries, release steps, and the current implementation status.
