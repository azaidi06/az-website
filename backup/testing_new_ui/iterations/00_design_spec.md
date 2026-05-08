# Design spec — "Editorial Serif + Mono Chrome"

Direction selected: **#6** from `research/01_design_directions.md`.

## Identity in one line
A two-typeface system: a neo-serif carries authorial voice; a data-grade
monospace carries technical credibility. Calm, hairline-driven layouts.
Light-first, with a real dark mode.

## Type
- **Display & body serif:** *Source Serif 4* (Google Fonts — free, variable, broad weights).
  Used for: page titles, headlines, prose, blog post titles.
- **UI & data monospace:** *JetBrains Mono* (Google Fonts — free).
  Used for: nav links, eyebrow labels, post metadata (date · category · read-time),
  pill tags, code, chart captions, footer.
- **Sans for utility chrome only:** *Inter* (already loaded site-wide), reserved
  for buttons and the tightest UI text where mono would feel heavy.

### Type scale (root 17px)
| Role            | Family        | Size (desktop) | Weight | Tracking |
|-----------------|---------------|----------------|--------|----------|
| Display XL hero | Serif         | clamp(56px, 9vw, 132px) | 400 | -0.02em |
| Display L       | Serif         | clamp(40px, 5vw, 72px) | 400 | -0.015em |
| H1 page         | Serif         | 44px           | 500   | -0.01em  |
| H2 section      | Serif         | 30px           | 500   | -0.005em |
| H3              | Serif         | 22px           | 500   | 0        |
| Eyebrow / label | Mono uppercase| 12px           | 500   | 0.12em   |
| Body            | Serif         | 18px / 1.65    | 400   | 0        |
| Meta / chrome   | Mono          | 13px / 1.5     | 400   | 0        |
| Code            | Mono          | 14px           | 400   | 0        |

## Color
### Light (default)
- `--paper`         `#FAF8F4`   page background
- `--ink`           `#15171A`   primary text
- `--ink-mute`      `#5B5E63`   secondary text
- `--hairline`      `#D9D5CC`   1px rules / dividers
- `--surface`       `#F2EEE6`   hover surfaces / pills
- `--accent`        `#B0431F`   clay (links, in-text emphasis)
- `--accent-link`   `#0F4C81`   prussian blue (alt link, very sparing)

### Dark
- `--paper`         `#101113`
- `--ink`           `#ECEAE3`
- `--ink-mute`      `#8E8F8C`
- `--hairline`      `#26272B`
- `--surface`       `#1A1B1F`
- `--accent`        `#E8945A`   warmer clay for dark contrast
- `--accent-link`   `#7AB8E8`

## Layout primitives
- 12-col grid, max-width 1200px, gutter 24px desktop / 16px mobile.
- Outer page padding: 64px desktop / 24px mobile.
- Vertical rhythm: 8px base; section gaps 96 / 64 / 32 (desktop / tablet / mobile).
- **No drop shadows.** Depth comes from 1px hairlines and 8% surface tints.
- **No rounded cards.** Borders are full-width 1px hairlines stacked vertically;
  cards use only top + bottom hairlines, never floating boxes.

## Components
- `.eyebrow` — mono caps, 12px, tracked, sits above any major heading.
- `.rule` — 1px hairline, `var(--hairline)`.
- `.meta-row` — mono 13px, items separated by ` · `, lowercase.
- `.tag` — mono 11px, no border, optional underline-on-hover.
- `.row-link` — full-width hairline-bounded list item; left = serif title, right = mono date. The default for blog/portfolio entries instead of cards.
- `.pill-toggle` — mono, hairline border, used for filtering.
- `.cta` — text-only with a mono prefix (`→ `) and a fade-in underline.

## Motion
- 180ms cubic-bezier(0.2, 0.7, 0.1, 1) on hover/focus only.
- Fade-up + 8px y-translate on intersection for hero blocks; threshold 0.15.
- Sticky TOC on long pages; current section gets a left hairline mark.
- One mono blinking caret in the hero status line. Nothing else animates.

## Globals
- Smooth scroll, but `prefers-reduced-motion` disables intersection animations.
- Selection color: clay accent at 22% opacity.
- Focus ring: 2px clay outline, 2px offset.
- Cursor: default (no custom cursor — would fight the calm).

## Page architecture (target)
- **Index:** full-bleed hero (display serif "Ali Zaidi"), mono status row beneath ("Currently · ML at …"), then a `featured-work` rail (3 hairline-row items), then `recent-writing` rail (5 hairline-row items), then `now` block. No cards.
- **About:** narrow column, serif prose, no icon grid. Tags as mono pills.
- **Blog:** mono filter pills + hairline list; no thumbnails unless they are *actual* charts. Date right-aligned.
- **Portfolio:** same hairline-row pattern. One row per project. Hover reveals abstract.
- **Resume:** existing structure, retypeset. Tabular-numerals for dates. Hairline section dividers.

## Things explicitly removed
- Bootstrap card chrome.
- "Powered by Quarto" footer.
- The "Brutal Design" navbar item (move to a tiny footer link).
- The bottom "Explore other landing page versions" block on index.
- AOS.js library (replaced with native IntersectionObserver, ~10 lines).

## Acceptance criteria for the iteration loop
After each iteration, the screenshot of every page must satisfy:
1. The same fonts and palette are visible across all pages.
2. No Bootstrap card with rounded corners visible anywhere.
3. Hero pulls focus immediately, then directs to writing.
4. Dark mode is recognizably the same site, not auto-inverted.
5. Mobile screenshot shows the hairline-row pattern collapsing cleanly.
