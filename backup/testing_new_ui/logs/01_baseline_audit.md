# Baseline audit — 2026-05-08

Captured 20 screenshots: 5 pages × {desktop, mobile} × {light, dark}.
See `screenshots/baseline/`.

## Per-page findings

### index.qmd (landing)
- Hero ("Bringing Data to Life") sits inside Quarto's narrow `article` column. Looks like a blog post intro, not a portfolio landing.
- Image of arch is decorative but cropped awkwardly inside the column.
- Subtitle is three labels stacked on top of a paragraph — fights for attention.
- Four feature cards (`About / Blog / Resume / Areas of Interest`) are flat Bootstrap cards with thin grey borders. Last one is dead-end (no link).
- Footer-of-page lists "Brutal Design / Gradient + Particles" — exposes scaffolding.

### about.qmd
- Photo + bio at top, then a 6-card "skills" grid. The cards are a different visual language from the landing cards. Icons feel like clipart.
- Container width is full-width but content is cramped to ~700px.

### blog.qmd
- Grid layout is OK in concept; image thumbnails are broken (black `X` placeholders) for several posts.
- No filtering, no tags shown, no search affordance even though Quarto can do it.

### portfolio.qmd
- 4 project cards in a 2×2. Tons of dead space. Cards are styled differently from About cards (icon left, tags below).
- Title "Portfolio / Selected projects and interactive analyses" is large but isolated.

### resume.qmd
- Plain serif body text, narrow column, sticky right-side TOC. Functionally OK but visually monotone — same weight headings, no rhythm.

## System-level problems
1. **No design system.** Three different card styles across three pages.
2. **Container/width inconsistency.** Index is article-narrow, portfolio is wide, about is in between.
3. **Type hierarchy is weak.** All h1s look the same. No display face. No scale.
4. **Color is accidental.** Only color signal is the green active-nav link from cosmo.
5. **Footer leaks engineering** ("Powered by Quarto"), and index footer leaks alt landing pages.
6. **Dark mode is untuned** — see `*_dark.png`. Same Bootstrap dark, no character.

## What we want from the overhaul
- One coherent visual identity across all pages.
- A landing that signals "researcher who ships," not "Bootstrap template".
- Confident typography. Real hierarchy.
- Restrained color palette with one strong accent.
- A repeating module set: `hero / section header / card / list-item / pill / link`.
- Dark mode that feels intentional (not auto-inverted).
- No leaked scaffolding (alt landing links, "Powered by Quarto").
