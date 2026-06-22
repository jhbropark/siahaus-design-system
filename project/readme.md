# SIA.HAUS — Design System

> **기술은 도구이고, 경험은 감각입니다.** — Technology is a tool. Experience is a sensation.

A design system for producing **premium, Keynote-grade presentation decks** for SIA.HAUS, a Seoul-based immersive-media studio. It is engineered for: **DOOH media projects, media-art festivals, immersive experiences, and medical-animation proposals.**

The aesthetic target is explicit: **Apple Keynote polish · Tesla investor-deck restraint · McKinsey data discipline.** Minimal text, large typography, dark backgrounds, premium architecture photography, data-driven layouts. The working ratio is **70% visual / 30% text** — every slide should breathe.

---

## 1. Company context

SIA.HAUS ("base on Seoul", `sia@sia.haus`) designs and engineers landmark media experiences — **media facades, projection mapping, media A/V, sound design, and media art.** Their structure spans the full pipeline: **Planning → Pre-Production → Production → Operation**, integrating commercial and artistic work toward sustainable IP businesses.

**Selected track record** (from the brief): KIA *Journey of Reflection* (Milan Design Week 2026), LG NLC *History Walk*, Venice Biennale *Time for Trees* (2025), FILA Holdings Heritage Lounge, SM/RIIZE *Lucky* MV, The Hyundai Seoul *Entropy of Nature* (2024), Seoul Light Gwanghwa, Lotte Jamsil media facade (819㎡, 21m×39m), Netflix *Love Alarm* zone, Samsung *LUX Soundroom*, and many more dating to 2018.

### Sources provided
- **`uploads/brief.pdf`** (copy of `sia.haus (hmp) brief -ing.pdf`) — 73-page company/portfolio brief. Primary source for tone, copy, and track record.
- **`uploads/sia.png`** — wordmark on white.
- **`uploads/sia-png.png`** — wordmark, black on transparent. Source for the trimmed/tinted logo assets in `assets/`.
- **`브랜드자산/`** — mounted brand-asset folder (mirrors the uploads above).

No codebase, Figma, or existing deck template was supplied — the visual system below is an original interpretation built to the brief's stated references, anchored on the real wordmark and the studio's voice.

---

## 2. Content fundamentals

How SIA.HAUS writes, derived from the brief:

- **Bilingual, Korean-led.** Long-form description is in Korean; headlines, client/section labels, and category tags are in English. A premium deck mixes both: an English kicker + Korean body, or vice-versa.
- **Aphoristic headlines.** The master line — *"Technology is a tool. Experience is a sensation."* — sets the register: short, declarative, sensory. Headlines are statements, never feature lists.
- **Sensory, spatial vocabulary.** Copy talks about *감각 (sensation), 몰입 (immersion), 빛 (light), 공간 (space), 경험 (experience)* — turning surfaces into canvases. Avoid dry ad-tech language.
- **Voice = "we", quietly confident.** Korean body uses the polite formal ending *—습니다*. It states what was built and why it mattered, without hype. English is terse and lowercase-leaning in labels.
- **Casing.** Display headlines use sentence case. Labels, kickers, client/agency tags, and data captions are **UPPERCASE mono, tracked wide**. The wordmark is always lowercase: `sia.haus`.
- **No emoji. Ever.** The only glyph "decoration" is the mono `//` marker before a section kicker, and unicode arrows (↑ ↓) for deltas.
- **Numbers carry weight.** Scale is the proof — ㎡, %, ₩, CAGR, years. Pair one big figure with one short caption; never crowd a slide with stats.

**Example kicker + headline:**
> `// CASE STUDY — 2026`
> **Journey of Reflection**
> ‘Opposites United’ 브랜드 철학을 공간 경험으로 구현한 기아의 EV 비전 전시.

---

## 3. Visual foundations

**Mood:** gallery-grade, architectural, nocturnal. The deck feels like a darkened exhibition hall where light and type are the only objects.

- **Color.** Monochrome backbone — deep **ink** backgrounds (`#08090A`–`#2A2E35`) and warm **paper** whites (`#FAFAF7`–`#6E7075`). One chromatic accent: **champagne `#C9A86A`**, the warmth of architectural lighting, used sparingly for emphasis, a single hero number, or a CTA. Data viz uses a muted **spectral** palette (amber/slate/violet/sage/rose) — a quiet nod to synesthesia. Backgrounds are **dark-first**; light mode is not a goal.
- **Type.** **Pretendard Variable** carries display + body (bilingual KR/EN), set **thin (100–300) and tight (-0.03em) at large sizes** for hero moments, neutral 400 for body. **IBM Plex Mono** handles every kicker, label, index, and data caption — uppercase, tracked `0.08–0.28em`. Hero type runs 96–136px; slide titles 64px; body 22px. Nothing below ~13px.
- **Spacing.** 8px base grid, **generous** outer margins (88px on a 1280×720 stage). Negative space is the design. Content is anchored to margins or vertically centered — never crammed.
- **Backgrounds & imagery.** Full-bleed **architecture / media-facade photography** is the hero medium, treated cool and low-key (`--img-filter`: slightly desaturated, dimmed) with a subtle **grain** overlay for filmic depth. Legibility comes from **protection scrims** — bottom or left gradients (`--scrim-bottom` / `--scrim-left`) — never a flat box over the photo. *(This system ships tonal placeholders; drop in real photography.)*
- **Borders & cards.** **Hairlines, not boxes.** Dividers and card edges are 1px `--line` (`#2A2E35`). Cards are a barely-raised ink surface (`--surface`) with a hairline border and near-square corners — no heavy fills.
- **Corner radii.** Restrained and near-square: 2–8px on UI, 0 on full-bleed and dividers. Pills (999px) only for tags and progress tracks. Premium = sharp.
- **Shadows.** Avoided on slides; depth comes from surface lightness + hairlines. Floating UI uses deep, soft, low-opacity shadows (`--shadow-md/lg`). A champagne **glow** (`--glow-accent`) marks active/emphasis states only.
- **Transparency & blur.** Glass (`--glass` + `--blur-md`) is reserved for overlays / lower-thirds floating over photography — not for decorative panels.
- **Motion.** Cinematic and restrained. Primary easing `--ease-out` (`cubic-bezier(0.16,1,0.3,1)`) — a slow settle. Durations 160–900ms. Entrances are **fades + small upward slides**; data bars grow on reveal. **No bounce, no spring, no infinite loops** on content.
- **Hover / press.** Hover = brighten border (`--line` → `--line-strong`) + a 2px lift on cards; buttons shift background. Press = `scale(0.98)`, no color flash. Subtle throughout.

---

## 4. Iconography

The brand is **typographic, not iconographic** — the source materials use essentially no icons. Honor that:

- **Default to glyphs, not icons.** The mono `//` section marker and unicode arrows **↑ ↓** (deltas) are the entire "icon" vocabulary. The `·` middot and `—` em-dash separate metadata.
- **No emoji, ever.** Not in decks, not in UI.
- **If functional icons are genuinely needed** (rare — settings, navigation, play/pause on a media slide), use **Lucide** via CDN (`https://unpkg.com/lucide@latest`) — thin 1.5–2px stroke, square caps, which matches the wordmark's light geometric line. **This is a substitution** (the brand ships no icon set); keep icons monochrome `--text-muted`, ~20–24px, and sparse. *Flagged — replace with a brand set if one exists.*
- **Logo.** The `sia.haus` wordmark is the primary brand mark. Assets in `assets/`:
  - `wordmark-white.png` — **primary**, on ink.
  - `wordmark-black.png` — on paper / light.
  - `wordmark-champagne.png` — accent contexts only.
  - `lockup-light.png` — original on-white lockup.

---

## 5. Index / manifest

**Root**
- `styles.css` — global entry point (consumers link this). `@import` manifest only.
- `readme.md` — this guide.
- `SKILL.md` — Agent-Skill front matter for portable use.

**`tokens/`** — `fonts.css` (Pretendard + IBM Plex Mono @font-face, CDN), `colors.css`, `typography.css`, `spacing.css`, `effects.css`, `base.css`.

**`assets/`** — wordmark variants (white / black / champagne) + on-white lockup.

**`guidelines/`** — foundation specimen cards (Design System tab): colors (ink, paper, champagne, spectral, signal), type (display, body, mono), spacing (scale, radii, elevation), brand (wordmark, motion).

**`components/`** — reusable React primitives (namespace `SIAHAUSDesignSystem_61fe1c`):
- `core/` — **Button**, **Tag**, **Card**, **Eyebrow**
- `data/` — **Stat** (hero metric), **BarMeter** (budget/KPI bar)

**`slides/`** — eight Keynote-grade slide templates @ 1280×720, sharing `slide.css`:
`01-Cover` · `02-ExecutiveSummary` · `03-MarketOpportunity` · `04-CaseStudy` · `05-Timeline` · `06-Budget` · `07-Proposal` · `08-KPIDashboard`

---

*Built to the brief; anchored on the real `sia.haus` wordmark and the studio's bilingual voice. Photography is placeholdered — drop in real architecture / media-facade imagery to finish.*
