# Personal site overhaul — final report

Run: 2026-05-08 · Scope: full visual redesign of `az-website` (test environment).
Direction: **Editorial Serif + Mono Chrome** (research direction #6).

## Before → after at a glance

|              | Baseline                                                  | After                                                            |
|--------------|-----------------------------------------------------------|------------------------------------------------------------------|
| Identity     | three different visual languages across pages             | one disciplined serif + monospace system, end to end             |
| Hero         | small Bootstrap hero in narrow article column             | full-bleed editorial wordmark, mono status row with caret        |
| Cards        | thin grey Bootstrap cards, three different styles         | hairline rows — same module on index, blog, portfolio             |
| Blog         | broken thumbnail grid                                     | numbered hairline list, serif titles, italic descs, mono dates   |
| About        | photo + 6 generic icon cards                              | photo + lead, prose, mono key/value "at a glance," reflection    |
| Portfolio    | sparse 4-card grid in dead space                          | full-width hairline rows with mono pills                         |
| Resume       | plain serif, monotone hierarchy                           | retypeset with hairline section dividers, mono dates             |
| Dark mode    | auto-inverted Bootstrap                                   | re-tuned tokens (paper → ink, clay shifts to warm orange)        |
| Navigation   | "About Me / Blog / Portfolio / Resume / Brutal Design"    | "about / writing / work / cv" — lowercased mono                  |
| Footer       | "Powered by Quarto"                                       | "© 2026 ali zaidi · azaidi06@gmail.com"                          |

Side-by-side screenshots: `screenshots/baseline/` vs `screenshots/iter02/`.

## What's in this folder

```
testing_new_ui/
├── REPORT.md                          ← you are here
├── screenshot.py                      ← playwright helper (file://-driven)
├── research/
│   └── 01_design_directions.md        ← 6 named directions + recommendation
├── iterations/
│   └── 00_design_spec.md              ← type/color/layout tokens, components, motion
├── logs/
│   ├── 01_baseline_audit.md           ← per-page findings on the original site
│   ├── 02_iter01.md                   ← first cut, defects to fix
│   └── 03_iter02.md                   ← what changed, lessons learned
└── screenshots/
    ├── baseline/                      ← 20 PNGs (5 pages × desktop+mobile × light+dark)
    ├── iter01/                        ← 20 PNGs
    └── iter02/                        ← 20 PNGs (final state of this session)
```

## Files actually changed in the project

- `redesign.css` — **new**, ~640 lines. The whole design system.
- `index.qmd` — rewritten as a full-bleed hero + two hairline rails + a "Now" block.
- `about.qmd` — rewritten with proper prose and a mono key/value at-a-glance block.
- `blog.qmd` — full-page listing, no thumbnails, hairline rows with numbered items.
- `_quarto.yml` — added `redesign.css` to the CSS array, lowercased nav, dropped "Brutal Design" from main nav, cleaned footer.
- (`portfolio.qmd`, `resume.qmd`: unchanged source — restyled entirely via CSS.)

`styles.css` was left intact as a reference/fallback so the redesign can be reverted by removing one line from `_quarto.yml`.

## How the design is organized

**Type:** Source Serif 4 (display + body) + JetBrains Mono (UI, metadata, code).
**Palette:** paper `#FAF8F4`, ink `#15171A`, clay `#B0431F` accent, hairline `#D9D5CC`.
**Dark:** `#101113` / `#ECEAE3` / warm-orange `#E8945A`.
**Layout:** 1200px max content rail, 80px num gutter shared by section-heads and row-links.
**Motion:** fade-up on intersection, mono caret blink in hero, hover slide on row-link arrows.

Full spec in `iterations/00_design_spec.md`.

## What's deliberately not done

- **No dev-server testing of interactivity.** Playwright opened the rendered HTML via `file://`. Anchor scrolls, search, and Quarto-rendered notebooks should be sanity-checked by the user.
- **`brutal.qmd` and `old_index_backup.qmd` were left in place.** Both are still routable; they're just removed from the main nav. Deleting them is a separate decision.
- **Hero copy is plausible but not verified.** I wrote "Currently cofounding EagleSwing — computer vision for golf — and previously at Lawrence Berkeley National Laboratory" by reading the resume. The user should review for tone and accuracy.
- **One mobile nit:** at 390px, the hero eyebrow sits ~6px under the navbar's bottom edge, where it's slightly hard to read against the blurred nav background. Easy fix in a follow-up — bump `clamp(120px, ...)` to `clamp(140px, ...)`.

## How to revert

```bash
# Drop redesign.css from the css array in _quarto.yml,
# revert index.qmd, about.qmd, blog.qmd, _quarto.yml, then:
quarto render
```
The original files are still in git.

## How to keep iterating

1. Edit `redesign.css` and the `.qmd` files.
2. `rm -rf .quarto/_freeze _site/index.html` then `quarto render` (the cache pollution issue documented in `logs/03_iter02.md` came back twice — when in doubt, nuke `.quarto/`).
3. `python testing_new_ui/screenshot.py testing_new_ui/screenshots/iterNN --label iterNN --site-dir _site`.
4. Diff against `screenshots/iter02/` to see what moved.
