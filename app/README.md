# 왕송호수 레일바이크 야간 미디어아트 도입 제안 — SIA.HAUS Deck

A real, runnable implementation of the 15-slide premium dark proposal deck
designed in Claude Design (see `../chats/chat1.md` and the original prototype
under `../project/`). Rebuilt on **Vite + React**, pixel-matched to the
prototype, replacing Claude Design's proprietary `deck-stage` runtime with a
self-contained scaler + keyboard navigation.

## Run

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # production build → dist/
npm run preview  # preview the production build
```

## Navigation

- **← / →** (or **Space / PageUp / PageDown**) — previous / next slide
- **Home / End** — first / last slide
- **F** — toggle fullscreen
- The bottom progress bar and on-canvas controls appear on hover.

## Routes

The app is a minimal hash router (`src/App.jsx`):

- **`#/`** — the 왕송호수 proposal deck (default).
- **`#/library`** — the design-system showcase: 6 React components + 8 reusable slide templates. Reachable via the **Library →** link (top-left of the deck, on hover).

## Structure

- `src/App.jsx` — hash router; toggles body scroll between the fixed deck and the scrolling library.
- `src/Deck.jsx` — deck shell: fits the fixed 1280×720 canvas to the viewport, keyboard + button navigation.
- `src/slides/index.jsx` — the 15 proposal slides (`SLIDES`), ported pixel-for-pixel from the design bundle.
- `src/slides/chrome.jsx` — shared slide chrome (mono kicker, page number, wordmark watermark).
- `src/components/` — the 6 design-system components (`Button`, `Card`, `Eyebrow`, `Tag`, `BarMeter`, `Stat`), copied verbatim from `../project/components/`. Barrel: `components/index.js`.
- `src/templates/index.jsx` — 8 reusable slide templates (`TEMPLATES`: Cover, Executive Summary, Market, Case Study, Timeline, Budget, Proposal, KPI). Frame CSS in `slide.css`, per-template CSS in `templates.css`. Root class is `.tslide` (not `.slide`) to avoid colliding with the deck.
- `src/Library.jsx` — the showcase page; `src/CanvasFrame.jsx` scales each 1280×720 template into a responsive thumbnail.
- `src/styles/` — the SIA.HAUS design tokens (colors, typography, spacing, effects, fonts), copied verbatim from `../project/tokens/`. `styles.css` is the `@import` manifest.
- `src/deck.css` / `src/library.css` — deck runtime + library chrome.
- `src/assets/` — the SIA.HAUS wordmark.

## Notes

- **Fonts** are CDN-hosted (Pretendard Variable + IBM Plex Mono via jsDelivr), matching the design bundle. Pretendard covers both Korean and Latin. Provide local binaries if you want them self-hosted.
- **Korean wrapping** uses `word-break: keep-all` + `text-wrap: pretty` globally, so lines break only at word boundaries (어절 단위) — the fix the user requested in the design chat.
- Cover photography is a tonal radial placeholder (as in the prototype). Drop a real 왕송호수 / 레일바이크 / media-art image into the Cover slide's backdrop to land the 70%-visual goal.
