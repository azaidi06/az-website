# 01 — Design Directions for Ali Zaidi's Portfolio

Research date: 2026-05-08
Context: Owner is an Applied Data Scientist / SWE / Product Leader. Site needs to read as intelligent, current, and editorially confident — not corporate-bland. Tennis-data-analysis blog is a key surface and benefits from a layout that frames long-form, chart-heavy posts as serious work.

The current site (Quarto + cosmo + a separate `brutal.css` experiment) is fragmented: a generic Bootstrap card grid on the landing page, a half-committed brutalist alternate, and no consistent typographic system. The directions below are coherent alternatives — each could be implemented end-to-end and would feel intentional.

---

## Direction 1 — "Research Lab Notebook"

A serif-led, paper-inspired aesthetic borrowing from Distill.pub and the NYT/Pudding/Bloomberg data-journalism canon. Long measure, generous leading, figure captions in small caps, footnotes in the margin. Charts are first-class citizens: full-bleed, sometimes breaking the text column. Light, warm off-white background; ink-black body; one restrained accent (a saturated tennis-clay orange or court-blue) used only for hyperlinks, in-text figure callouts, and chart highlights.

**Why it fits.** Tennis analysis posts already are essays with figures — this direction treats them as the marquee, not as appendices to a CV. Signals "I write things worth reading" rather than "I have a portfolio."

**Type:** *Tiempos Text* or *Source Serif 4* for body; *Inter* or *GT America* for UI chrome; *JetBrains Mono* for code/data labels.
**Palette:** background `#FBF8F3`, ink `#171513`, rule `#E4DDD0`, accent `#C8542B` (clay), link-blue `#0A4F8F`.
**Motion:** almost none — only a sticky table-of-contents that highlights as you scroll, and chart elements that fade in on intersection.

**References:**
- https://distill.pub/2020/circuits/zoom-in/
- https://pudding.cool/
- https://colah.github.io/

---

## Direction 2 — "Terminal Brutalism"

A dense, monospace-first interface that reads like a well-typeset terminal. Everything aligns to a fixed character grid. Section headers use `## NAME` markdown-style labels. ASCII rules (`────────`) replace decorative dividers. Posts list as a tabular log: date · category · title · word-count, hover reveals the abstract inline. Default to dark mode (works well for the tennis-data audience that lives in notebooks).

**Why it fits.** A monospace-driven layout is honest about the work — this is someone who reads CSVs and writes Python. It is also currently fashionable in the developer-tool world (Vercel, Linear, Raycast, Rauno) without being a meme. Done with restraint, monospace conveys precision rather than gimmick.

**Type:** *Berkeley Mono* (or *JetBrains Mono* / *Geist Mono* as free alternatives) for everything; *Geist Sans* for the rare display moment.
**Palette (dark):** background `#0B0B0C`, surface `#141416`, text `#E6E4DE`, dim `#6F6E6A`, accent `#9DFF7B` (terminal green) used sparingly; light-mode inverse: `#F4F2EC` / `#0B0B0C` / `#1B5E20`.
**Motion:** caret-blink cursors on focused links, character-by-character text reveal on hero only, otherwise static.

**References:**
- https://rauno.me/
- https://vercel.com/font (Geist showcase)
- https://linear.app/

---

## Direction 3 — "Editorial New / Display Serif"

A fashion-magazine cousin of Direction 1: huge display serif headlines (60–160px viewport-scaled), tight letter-spacing, set against a near-white page with a strict 12-column grid. Body in a clean neo-grotesque. Posts presented as numbered items (`№ 014`) with oversized titles and thin metadata rules. One subtle texture (CSS noise / film grain) gives the page tactility without 3D weight.

**Why it fits.** Reads as confident and contemporary, the way the best Awwwards portfolios do in 2026. It elevates a tennis-data blog from "hobby project" to "publication." Risk: can tip into agency-pretentious if the writing doesn't hold up — Ali's writing does.

**Type:** *PP Editorial New* (Ultralight + Italic) display; *Söhne* or *Inter* body; *GT America Mono* for metadata, dates, captions.
**Palette:** paper `#F6F4EE`, ink `#111`, hairline `#D6D2C7`, single hot accent `#FF3D00` for hover/active only.
**Motion:** scroll-triggered weight/width axis variation on the marquee headline (variable-font morphing), cursor-following hover area on cards, otherwise calm.

**References:**
- https://www.awwwards.com/websites/?tag=portfolio&typography=Editorial+New
- https://pangrampangram.com/products/editorial-new
- https://muz.li/blog/top-100-most-creative-and-unique-portfolio-websites-of-2025/

---

## Direction 4 — "Swiss Grid + Data"

International Typographic Style applied to a personal site. Strict modular grid visible as 1px hairlines on hover. Left-aligned everything. Numerals in tabular form. Charts and content blocks share the same grid, so a Plotly figure literally aligns to the same column rhythm as the prose around it. No images of the author hero-style; instead, a small structured "index card" data block (`Role / Location / Currently / Writing`).

**Why it fits.** A grid that can hold both prose *and* data visualizations is exactly what a tennis-analysis site needs. It also signals taste without shouting — this is what Stripe and Linear borrow from. Avoids both bland-corporate and try-hard-brutalist.

**Type:** *Neue Haas Grotesk* / *Inter Display* throughout; *JetBrains Mono* for tabular numerals and code.
**Palette:** white `#FFFFFF`, near-black `#0F0F10`, neutrals `#8A8A8A` / `#E4E4E4`, ATP-blue accent `#1D4ED8`, WTA-magenta accent `#E11D48` (used to encode tour, never decoratively).
**Motion:** grid lines fade in on hover, charts animate in with a 1px stroke draw, page transitions instant.

**References:**
- https://stripe.com/
- https://linear.app/
- https://www.setproduct.com/blog/complete-guide-to-blueprint-grid-design

---

## Direction 5 — "Tactile Brutalism done well"

Heavy borders, no rounded corners, visible structure, Z-index layered cards that overlap. Acid-bright accents on near-black surfaces. The "brutal" current site already gestures at this but reads as raw rather than designed. Done with discipline (Pangram Sans Rounded headlines, generous internal padding, only two acid colors), it can be a strong signature.

**Why it fits.** Owner has already been pulled toward this vibe (`brutal.css`). It is also genuinely 2026 (per Fireart, Muz.li, NN/g trend reports). Risk: harder to make tennis charts feel at home — the aesthetic competes with the data viz.

**Type:** *PP Neue Montreal* or *Söhne Breit* display; *IBM Plex Sans* body; *IBM Plex Mono* metadata.
**Palette:** `#0D0D0D` background, `#F2F2EC` cards, accents `#D8FF3E` (acid lime) + `#FF5C28` (orange).
**Motion:** card hover lifts with hard 8px shadow offset (no blur), scroll-pin section reveals.

**References:**
- https://brutalistwebsites.com/
- https://www.awwwards.com/awwwards/collections/brutalism/
- https://reallygooddesigns.com/neo-brutalist-website-examples/

---

## Direction 6 — "Hybrid: Editorial Serif + Mono Chrome"

The 2026 consensus pairing called out across multiple trend reports: an elegant neo-serif for headlines and prose, a data-grade monospace for metadata, dates, navigation, captions, and code. Light first with a deliberate dark mode. The serif carries authorial voice; the mono carries technical credibility. Subtle CSS noise on the background, thin 1px hairlines, no drop shadows.

**Why it fits.** It is the only direction that fully resolves the two halves of Ali's identity (writer + engineer) into one type system rather than picking a side. Charts and prose coexist because the mono captions match Plotly's natural look while the serif elevates the writing.

**Type:** *Tiempos Headline* or *PP Editorial New* (display); *Source Serif 4* (body); *Berkeley Mono* / *JetBrains Mono* (UI + meta).
**Palette:** paper `#FAF8F4`, ink `#15171A`, hairline `#D9D5CC`, accent `#B0431F` (clay), link `#0F4C81`; dark mode: `#101113` / `#ECEAE3` / `#E8945A`.
**Motion:** sticky TOC, fade-up on intersection, mono-cursor blink on the hero current-status line, nothing else.

**References:**
- https://www.ikagency.com/graphic-design-typography/typography-trends-2026/
- https://fireart.studio/blog/the-best-web-design-trends/
- https://maxibestof.one/typefaces/tiempos

---

## Recommendation — Direction 6 ("Editorial Serif + Mono Chrome")

Pick Direction 6. It is the sharpest fit for this specific site, not a compromise.

The core problem with the current site is incoherence — a serif-friendly tennis essay sitting next to a brutalist landing page next to a cosmo card grid. Direction 6 resolves that by giving the entire surface one disciplined two-typeface system: a neo-serif that takes the long-form tennis-data essays seriously, and a monospace that makes the navigation, post metadata, code samples, and chart captions feel native to a data scientist's hand. Nothing else in the field does both jobs at once. Pure-mono (Direction 2) under-sells the writing; pure-display-serif (Direction 3) under-sells the engineering; brutalism (Direction 5) fights the charts.

It is also the most defensible against trend-decay: serif + mono pairings are explicitly the dominant 2026 premium-web pattern in every trend report surveyed, and the underlying typography is timeless enough to outlive the trend window. The clay accent ties subtly to tennis without being literal. Implementation is straightforward in Quarto: two webfonts, a clean CSS reset, hairlines instead of cards, and a dark-mode swap that already exists in `_quarto.yml`.

---

## Source index

- https://karpathy.ai/
- https://colah.github.io/
- https://lilianweng.github.io/
- https://jalammar.github.io/
- https://distill.pub/
- https://pudding.cool/
- https://rauno.me/
- https://vercel.com/font
- https://linear.app/
- https://stripe.com/
- https://www.anthropic.com/research
- https://www.awwwards.com/websites/typography/
- https://www.awwwards.com/awwwards/collections/brutalism/
- https://muz.li/blog/top-100-most-creative-and-unique-portfolio-websites-of-2025/
- https://muz.li/blog/web-design-trends-2026/
- https://fireart.studio/blog/the-best-web-design-trends/
- https://reallygooddesigns.com/web-design-trends-2026/
- https://www.ikagency.com/graphic-design-typography/typography-trends-2026/
- https://artcoastdesign.com/blog/typography-branding-trends-2026
- https://madegooddesigns.com/trending-fonts/
- https://www.setproduct.com/blog/complete-guide-to-blueprint-grid-design
- https://shikun.io/projects/clarity
- https://pangrampangram.com/products/editorial-new
- https://maxibestof.one/typefaces/tiempos
- https://maxibestof.one/typefaces/editorial-new
- https://maxibestof.one/typefaces/gt-america-mono
- https://basement.studio/post/the-birth-of-geist-a-typeface-crafted-for-the-web
- https://github.com/vercel/geist-font
