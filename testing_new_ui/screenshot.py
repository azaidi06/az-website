#!/usr/bin/env python3
"""Headless screenshot helper for the local Quarto preview.

Usage:
    python testing_new_ui/screenshot.py <out_dir> [--label LABEL] [--port PORT]

Captures every key page at desktop + mobile, light + dark.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGES = [
    ("index", "/"),
    ("about", "/about.html"),
    ("blog", "/blog.html"),
    ("portfolio", "/portfolio.html"),
    ("resume", "/resume.html"),
]

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile":  {"width": 390,  "height": 844},
}

THEMES = ["light", "dark"]


def shoot(out_dir: Path, label: str, base_url: str) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            for theme in THEMES:
                ctx = browser.new_context(
                    viewport=vp,
                    color_scheme=theme,
                    device_scale_factor=1,
                )
                page = ctx.new_page()
                for slug, path in PAGES:
                    url = path if path.startswith("file://") or path.startswith("http") else base_url.rstrip("/") + path
                    fname = f"{label}_{slug}_{vp_name}_{theme}.png"
                    out_path = out_dir / fname
                    try:
                        page.goto(url, wait_until="networkidle", timeout=20000)
                        # Force theme via Quarto's data-bs-theme attr
                        page.evaluate(
                            f"document.documentElement.setAttribute('data-bs-theme', '{theme}');"
                        )
                        # Trigger any IntersectionObserver fade-ins, then force-clear inline opacity/transform
                        page.evaluate("""async () => {
                            const h = document.body.scrollHeight;
                            const step = window.innerHeight * 0.8;
                            for (let y = 0; y <= h; y += step) {
                                window.scrollTo(0, y);
                                await new Promise(r => setTimeout(r, 60));
                            }
                            window.scrollTo(0, 0);
                            await new Promise(r => setTimeout(r, 200));
                            // Force any animated-in elements to their final state for screenshot stability
                            document.querySelectorAll('[style*="opacity"], [style*="transform"]').forEach(el => {
                                el.style.opacity = '1';
                                el.style.transform = 'none';
                            });
                            await new Promise(r => setTimeout(r, 100));
                        }""")
                        time.sleep(0.4)
                        page.screenshot(path=str(out_path), full_page=True)
                        saved.append(str(out_path))
                        print(f"OK  {fname}")
                    except Exception as e:
                        print(f"ERR {fname}: {e}", file=sys.stderr)
                ctx.close()
        browser.close()
    return saved


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--label", default="snap")
    ap.add_argument("--port", default="4848")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--site-dir", default=None,
                    help="If set, screenshot via file:// from this directory instead of HTTP")
    args = ap.parse_args()

    if args.site_dir:
        site = Path(args.site_dir).resolve()
        # rewrite PAGES to use file:// + the rendered html paths
        global PAGES
        PAGES = [
            ("index", f"file://{site}/index.html"),
            ("about", f"file://{site}/about.html"),
            ("blog",  f"file://{site}/blog.html"),
            ("portfolio", f"file://{site}/portfolio.html"),
            ("resume", f"file://{site}/resume.html"),
        ]
        base = ""
    else:
        base = args.base_url or f"http://127.0.0.1:{args.port}"
    out = Path(args.out_dir)
    saved = shoot(out, args.label, base)
    print(f"\nSaved {len(saved)} screenshots to {out}")


if __name__ == "__main__":
    main()
