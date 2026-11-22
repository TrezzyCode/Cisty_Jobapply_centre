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
- Deliverables: music version and clean no-music version from the same timeline.
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
| 330–479 | 5.0 s | Station row embed | See the nearest MRT / LRT station — calculated and saved. |
| 480–629 | 5.0 s | Conversation list reveal | Track only the application conversations sent through Cisty. |
| 630–809 | 6.0 s | UI-to-brand morph | Cisty — Apply with clarity. by Trez |

## Safety and privacy

- No real Gmail account, OAuth credential, API key, resume path, contact or application database is opened.
- All captured companies, contacts and messages are fictional and generated only for this film.
- The isolated capture database is ignored by Git and deleted/replaced safely on every capture run.
