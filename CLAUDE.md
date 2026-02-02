# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands

This is a Quarto static website. Key commands:

- `quarto preview` - Start local development server with hot reload
- `quarto render` - Build full site to `_site/` directory
- `quarto render [file.qmd]` - Render a single file

## Project Structure

**Framework:** Quarto 1.7.33 static site generator

**Main Pages:**
- `index.qmd` - Landing page with hero section
- `about.qmd` - About page using Jolla template
- `blog.qmd` - Blog listing page (grid layout)
- `resume.qmd` - CV with HTML + PDF output

**Blog Posts:** Located in `posts/` directory. Each post is either a `.qmd` file or Jupyter notebook (`.ipynb`). Post-level config in `posts/_metadata.yml` sets `freeze: true` (caches computational output) and enables title block banners.

**Output:** Built site goes to `_site/` (gitignored except for committed files)

## Configuration

- `_quarto.yml` - Site config: navbar, footer, dual themes (cosmo light/darkly dark)
- `styles.css` - Custom CSS for hero sections, cards, animations, dark mode overrides
- `cv.css` - Resume-specific styling

## Styling Notes

- Uses AOS.js for scroll animations
- Custom fonts: Space Grotesk (headings), Inter (body)
- Responsive design with Bootstrap grid from Quarto
- Theme toggle between light/dark modes

## Deployment

- Main branch: `main`
- Deployment branch: `gh-pages` (GitHub Pages)
