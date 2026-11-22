# Cisty

## Run the approved glass interface

1. Install Python 3.10 or newer.
2. Run `install.bat` once. This installs PySide6 and the existing Excel/Gmail dependencies.
3. Run `run_glass_ui.bat`. It starts Cisty through `pythonw.exe`, so no command window remains open and Windows console selection cannot pause the app.

The new interface reads the same local database and settings as the existing application. Sent application state roams through the signed-in Gmail account using the private `Cisty/Applications` label. Sync runs only when the user clicks **Sync Gmail** and does not query/expose unrelated inbox, sent messages, or Gmail drafts.

The interface uses Qt-native frosted materials over restrained warm-gold and cool-white background light fields, with translucent controls, continuous edge highlights, a liquid-glass segmented tab control, physical button feedback, and short directional page transitions. A subtle planning grid lights and fades behind the cursor, while brief click sparks acknowledge the exact press location without covering the data layer. Windows 11 also receives the native Mica backdrop and rounded-window treatment. The sidebar sun/moon control switches immediately between the warm light theme and a composed black, white, and champagne-gold dark theme. Its original motion remains two interruptible timelines: a 300 ms sun/moon travel and a 500 ms sky/cloud/star transition. Theme colors use palette-backed styling and in-place widget refresh instead of reparsing the full QSS, so the 1,249-row company table no longer adds an artificial theme delay. The preference survives restart. Other UI motion follows the Windows reduced-motion preference; set `QT_REDUCE_MOTION=1` before launch to explicitly disable the authored theme-switch, cursor-grid, and click-spark movement too.

## Existing interface

`run.bat` still starts the previous Tkinter interface. Keep it as a fallback while the new Qt interface is being tested.

## Local data

Each Windows user has separate data under:

`%LOCALAPPDATA%\IT Internship Auto Apply`

This includes application history, settings, the database, Gmail authorization token, and the optional profile photo selected in My Workspace. The sidebar falls back to the user's initials when no photo is selected. Do not copy that folder when sharing the application with another person.

Profile data, API keys, resume paths, avatars, station calculations, Gmail draft state, and the imported company list remain local. Only Cisty-sent applications, replies, thread IDs, and send times are restored through Gmail. On another computer, import the company Excel and connect the same Gmail account, then use **Sync Gmail**. Existing users should sync once on the original computer first so its locally registered Cisty threads receive the roaming label.

Cisty allows one running instance per Windows account. If an unexpected GUI error occurs, details are appended to `%LOCALAPPDATA%\IT Internship Auto Apply\cisty_error.log` without deleting the local database.

## Packaging

The current PySide6 interface has not been packaged as an EXE yet. After it is tested on the target Windows resolutions, run `build_exe.bat`. The script creates `dist\Cisty.exe` and deliberately excludes local settings, databases, Gmail tokens, resumes, credentials, and profile photos.

After building, copy `dist\Cisty.exe` into `UserPack\`. The UserPack contains a no-admin installer, portable launcher, uninstaller, package checker, Gmail/Geoapify setup instructions, user guide, privacy notes, and troubleshooting guide. EXE and ZIP files inside UserPack are intentionally excluded from Git.

## Project handoff

See `HANDOFF.md` for architecture, privacy boundaries, release steps, and the current implementation status.

## Product promo

The `promo/` folder contains the 27-second Cisty Remotion product film, isolated fictional UI captures, audio provenance, shot plan, workbench manifest, and reproducible finalization script. The public GitHub edition has no background music and retains only restrained interface SFX. See `promo/README.md` before rendering.
