#!/usr/bin/env python3
"""Screenshot the 3 hero mocks across 3 themes (light / sepia / dark) at desktop."""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "_site"
OUT  = Path(__file__).resolve().parent / "screenshots" / "iter03_mocks"
OUT.mkdir(parents=True, exist_ok=True)

MOCKS = [
    ("a_bg",    f"file://{SITE}/explore-a.html"),
    ("b_split", f"file://{SITE}/explore-b.html"),
    ("c_plate", f"file://{SITE}/explore-c.html"),
]
THEMES = ["light", "sepia", "dark"]
VIEWPORT = {"width": 1440, "height": 900}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = ctx.new_page()
        for slug, url in MOCKS:
            for theme in THEMES:
                out = OUT / f"iter03_{slug}_{theme}.png"
                try:
                    page.goto(url, wait_until="networkidle", timeout=20000)
                    page.evaluate(f"""
                        document.documentElement.setAttribute('data-theme', '{theme}');
                        document.documentElement.setAttribute('data-bs-theme', {{
                            'light':'light','sepia':'light','dark':'dark'
                        }}['{theme}']);
                    """)
                    page.evaluate("""async () => {
                        const h = document.body.scrollHeight;
                        const step = window.innerHeight * 0.8;
                        for (let y = 0; y <= h; y += step) {
                            window.scrollTo(0, y);
                            await new Promise(r => setTimeout(r, 50));
                        }
                        window.scrollTo(0, 0);
                        await new Promise(r => setTimeout(r, 200));
                        document.querySelectorAll('[style*="opacity"], [style*="transform"]').forEach(el => {
                            el.style.opacity = '1';
                            el.style.transform = 'none';
                        });
                        await new Promise(r => setTimeout(r, 100));
                    }""")
                    time.sleep(0.4)
                    page.screenshot(path=str(out), full_page=True)
                    print(f"OK  {out.name}")
                except Exception as e:
                    print(f"ERR {out.name}: {e}")
        ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
