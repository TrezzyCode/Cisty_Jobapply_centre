# Cisty — Project Handoff

Last updated: 2026-11-22

## Product summary

Cisty is a Windows desktop application for importing a company Excel list, reviewing recruitment email candidates, calculating the nearest KL MRT/LRT/Monorail station, preparing Gmail applications, and following only the Gmail conversations created by this application.

The current primary interface is the PySide6 application in `qt_main.py`. The older Tkinter application in `main.py` remains the data and service layer as well as a temporary UI fallback.

## Run locally

1. Install Python 3.10 or newer.
2. Run `install.bat` once.
3. Run `run_glass_ui.bat` for the current interface.
4. `run.bat` starts the older Tkinter interface for fallback testing.

## Main files

- `qt_main.py` — current warm Apple-inspired PySide6 UI, Cisty startup animation, responsive layout, filtering, profile, station calculations, Gmail drafts/sending, and tracked conversations.
- `assets/` — approved Cisty squircle-C mark, lockup, app-icon SVG, and generated release icon files.
- `tools/generate_brand_assets.py` — deterministic PNG/ICO renderer used by `build_exe.bat`.
- `main.py` — shared constants, local-data paths, SQLite migrations, Excel import, and the older Tkinter interface.
- `CareeReX_IT_highlight.xlsx` — starter company workbook bundled as application data.
- `requirements.txt` — runtime dependencies.
- `build_exe.bat` — reproducible one-file Windows EXE build script. It is intentionally not run during active UI development.
- `UserPack/` — distribution-ready folder containing installation/portable scripts and end-user setup, privacy, usage, and troubleshooting documentation. Add the approved `Cisty.exe` here only after building.
- `.gitignore` — privacy boundary for personal data and build artifacts.

## Local data and privacy boundary

Every Windows account stores its own mutable data under:

`%LOCALAPPDATA%\IT Internship Auto Apply`

This includes the SQLite database, settings, Gmail authorization token, and optional profile avatar. Resume and OAuth credential paths point to the current user's own files. None of these may be committed, bundled, or copied to another user.

The application only syncs Gmail threads whose first message was sent through this application. Cross-device sent state uses the Gmail label `Cisty/Applications`; sync queries only that label ID and must not scan or display unrelated inbox/sent conversations or Gmail drafts. New messages include a stable company-name hash in `X-Cisty-Company-Key`; legacy labelled threads fall back to verified recipient and subject matching.

Never commit:

- `settings.json` or `user_data/`
- `*.db`
- Gmail/OAuth tokens or `client_secret*.json`
- resumes (`*.pdf`, `*.docx`)
- `.env` files, API keys, or profile photos
- `build/`, `dist/`, `*.spec`, `__pycache__/`

## Current feature status

- Excel import and email-candidate matching are implemented; candidates require user verification.
- Industry, region, distance, transit-line, and application-status filters are implemented.
- Bulk station calculation respects the currently selected industry and region.
- Calculated station data is stored in SQLite and is reused; recalculation overwrites the previous result.
- Supported transit networks include MRT Putrajaya, MRT Kajang, LRT Kelana Jaya, LRT Ampang, LRT Sri Petaling, and KL Monorail.
- Gmail draft, reviewed send, tracked-thread refresh, and reply are implemented.
- Gmail roaming sync is implemented for school/home/new-PC use as an explicit, cancellable **Sync Gmail** action. It restores Applied/Replied state, timestamps, and tracked conversations. It has a 20-second request timeout, reports progress, does not scan drafts, and checks the connected account against My Workspace. Do not reintroduce startup or periodic full-mailbox work.
- Post-sync table refresh reuses existing `QTableWidgetItem` instances and suspends painting during the batch. This is required for the 1,249-row company list: replacing every cell after Gmail sync previously blocked the GUI long enough for Windows to report Cisty as unresponsive. Gmail sync progress, completion, cancellation, and errors are reported inline beside the button; do not restore a modal completion/error dialog, because a hidden modal can make the main window appear frozen even when its event loop is healthy.
- `run_glass_ui.bat` resolves and launches `pythonw.exe` so a selected/QuickEdit console cannot suspend the GUI. `QLockFile` prevents concurrent instances, and unhandled GUI exceptions are appended to `%LOCALAPPDATA%\IT Internship Auto Apply\cisty_error.log`.
- Light/dark appearance is tokenized in `LIGHT_THEME` / `DARK_THEME`. Dark mode uses near-black surfaces, bone-white type, and restrained champagne-gold action/selection accents. The custom `ThemeSwitch` preserves the supplied control's layered cloud exit, star entrance, sliding moon, halo depth, hover nudge, and interruptible reversal. Its authored timing uses separate 300 ms thumb and 500 ms atmosphere animations. Theme QSS is palette-backed and installed once; switching themes updates widget palettes and repolishes existing widgets in place. Do not restore the former delayed full-QSS reparse or put a `QGraphicsOpacityEffect` on the root window—both make the 1,249-row table feel unresponsive. It persists `settings.json` → `theme`, compacts with the sidebar, and updates the Windows immersive title bar. Because Windows reported client-area animations disabled on the design machine even though these effects were explicitly requested, the switch, cursor grid, and click sparks play by default and use `QT_REDUCE_MOTION=1` as their explicit opt-out; other application motion still follows the Windows setting. Keep future colors semantic rather than adding component-local hex values.
- `GlassFrame`, the animated `QPushButton`, `FluidTabBar`, `AnimatedStack`, `Backdrop`, and `ClickSparkOverlay` form the native liquid-glass interaction layer. They provide translucent material depth, continuous specular edges, press compression/release, a glass segmented tab lens, directional page continuity, cursor-local grid illumination, click sparks, and bounded background glow without adding a web runtime. The grid is painted behind the content so it cannot cross table text; sparks are a transparent foreground layer and never intercept input. Every custom `QPainter` must be explicitly ended before calling a Qt base `paintEvent`; overlapping active painters caused a Windows access violation during development. Keep the bounded timers, reduced-motion branches, and native-window stress test when changing these components.
- My Workspace is embedded in the main window.
- The profile avatar can be selected or removed in My Workspace. The sidebar uses the same photo and falls back to the user's initials.
- The approved Cisty squircle-C mark is used by the startup reveal, window icon, and EXE packaging. The electric outline plays once and respects Windows reduced-motion settings.
- The light UI uses a warm Claude-like palette; dark mode is a deliberate black, bone-white, and champagne-gold composition. Both use restrained Apple-style depth and motion. Avoid excessive glass blur, gradients, glows, tilt effects, or decorative animation.

## Station-distance rules

Geoapify is used only for free-tier geocoding. Station coordinates come from free OpenStreetMap-backed data. The stored automatic distance is straight-line distance, not verified walking time. The user must open the map route and manually verify the final walking minutes before the route is marked verified.

## Build and release

Do not package during normal iteration. When a release candidate is approved:

1. Test `run_glass_ui.bat` at 860×560, 1366×768, 1920×1080, and a high-DPI scale such as 125% or 150%.
2. Test Excel import, a filtered station calculation, profile save/avatar, Gmail draft, and conversation refresh.
3. Confirm no personal data exists in the Git staged-file list.
4. Run `build_exe.bat`.
5. Copy `dist\Cisty.exe` to `UserPack\Cisty.exe`.
6. Run `UserPack\verify_package.bat` and test `install.bat`, shortcuts, portable launch, and uninstall on a clean Windows account.
7. Zip the complete UserPack folder. Never include or share `%LOCALAPPDATA%\IT Internship Auto Apply`.

## Git workflow

Canonical repository: `https://github.com/TrezzyCode/auto_send_internship_req`

Use the `main` branch. Before every push, inspect `git status` and the staged file list for credentials or personal data. Commit source and documentation changes together with a concise message. Do not commit generated EXE files unless a future release policy explicitly requests GitHub Releases.

## Product promo video

The reproducible Remotion project is in `promo/`. It uses real Cisty PySide6 captures generated from an isolated fictional database; no personal application data is used. `promo/capture_demo.py` can regenerate the captures.

Install Node.js, run `npm install` inside `promo/`, then run `npm run render`. The finalizer normalizes the music master and reuses the exact same encoded video stream for the no-music version. Final MP4 files are written to `promo/out/final/` and intentionally ignored by Git. Mixkit music and Freesound CC0 provenance are recorded under `promo/public/audio/`.

## Verification note

The native PySide6 build is checked with `py_compile`, offscreen material/animation captures, repeated rapid theme reversals, and a real Windows hidden-window stress launch before each approved UI handoff. Repeat the resolution and high-DPI checks above before packaging a release candidate.
