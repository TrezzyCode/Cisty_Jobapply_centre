# Cisty product film

This folder contains the reproducible 27-second, 1920×1080, 30 fps Cisty product promo.

## Privacy

`capture_demo.py` creates an isolated database in `capture_runtime/` before importing the application. Every company, email address, thread and profile field in the screenshots is fictional. The script never opens the user's real `%LOCALAPPDATA%\IT Internship Auto Apply` data.

## Build

```powershell
npm install
npm run render
```

`npm run render` creates both deliverables from one timeline:

- `out/final/cisty-promo.mp4`
- `out/final/cisty-promo-no-music.mp4`

The finalizer raises the verified music bed by 8 dB and copies the master's encoded video stream into the no-music file, so both variants are frame-identical. `out/`, local Node tools, dependencies and capture runtime are ignored by Git.

## Regenerate safe product captures

From the application folder:

```powershell
py -3 promo\capture_demo.py
```

## Project structure

- `DESIGN_SPEC.md` — creative direction and shot plan.
- `src/timeline.ts` — single source of truth for shot timing.
- `src/CistyFilm.tsx` — scenes, motion and audio cues.
- `src/workbench.ts` — video-shotcraft Workbench manifest.
- `scripts/finalize.mjs` — loudness finalization and deterministic dual-output muxing.
- `public/captures/` — real Cisty UI rendered from fictional data.
- `public/audio/` — source audio, licences, hashes and technical measurements.
