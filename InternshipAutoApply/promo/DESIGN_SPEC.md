# Cisty product film — design specification

## Creative direction

Three directions were considered:

1. **Warm Precision** — Cisty's real warm ivory workspace, terracotta accents, restrained Apple-like motion and editorial typography.
2. **Transit Editorial** — a denser railway-map language with line colours and map geometry.
3. **Launch Stage** — a darker, high-contrast product launch treatment.

**Selected: Warm Precision.** It preserves the product's personality and makes the software feel trustworthy, personal and calm. Transit geometry is used as a supporting motif, not as decoration competing with the interface.

## Format

- 1920 × 1080, 30 fps, 27 seconds.
- No voice-over. English on-screen copy matches the current English interface.
- Current public deliverable: clean no-music version with restrained interface SFX.
- Product imagery is captured from the real PySide6 application with a completely isolated fictional database.

## Visual system

- Canvas: `#F7F3EC` warm ivory.
- Primary ink: `#2B2724`; secondary ink: `#756C66`.
- Accent: `#B75334`; accent soft: `#EED8CB`.
- Surfaces: milky white with a warm 1 px outline and soft, wide shadow.
- Type: system sans / Segoe UI, large optical titles, compact supporting copy.
- The approved C mark is the only hero symbol.

## Motion system

- Primary easing: `cubic-bezier(0.23, 1, 0.32, 1)`.
- Product-camera moves are slow and intentional; no handheld shake.
- Interactions occur at human speed: typing, short pause, filter result, pointer confirmation.
- One dominant effect per shot. Motion blur is reserved for a fast landing or flip.
- Reduced-motion-friendly: all meaning remains in the held end states.

## Shot plan

| Frames | Duration | Shot | Product promise |
|---:|---:|---|---|
| 0–149 | 5.0 s | C mark stroke build | Your internship search, in one calm workspace. |
| 150–329 | 6.0 s | Type and filter | Import once. Filter by industry, region and transit line. |
| 330–479 | 5.0 s | Saved station detail with callouts | See the nearest MRT / LRT station — calculated and saved. |
| 480–629 | 5.0 s | Conversation list reveal | Track Cisty-only replies and keep application state synced between school and home. |
| 630–809 | 6.0 s | UI-to-brand morph | Cisty — Apply with clarity. by Trez |

## Requirements to execution

| Requirement | Execution decision |
|---|---|
| Import and filter by industry, region and transit line | Real filtered Cisty capture, human-speed typing, and explicit filter caption in frames 150–329. |
| Saved nearest station and distance | Real selected-company capture plus three readable floating fact callouts in frames 330–479. The callouts summarize the saved row; they do not claim to embed into it. |
| Cisty-only email conversation | Real conversation capture and an explicit `Cisty-only conversations` label in frames 480–629. |
| Same-Gmail school/home sync | `Same Gmail` callout and school/home status copy in the conversation shot. |
| No background music | `CistyPromoClean` composition; only three bounded, CC0 interface SFX cues remain. |
| Privacy-safe public media | All product captures are regenerated from the isolated fictional database in `capture_demo.py`. |
| Motion vocabulary | Custom Warm Precision motion; no Gallery card or variant is claimed. |

## Safety and privacy

- No real Gmail account, OAuth credential, API key, resume path, contact or application database is opened.
- All captured companies, contacts and messages are fictional and generated only for this film.
- The isolated capture database is ignored by Git and deleted/replaced safely on every capture run.
