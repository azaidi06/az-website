#!/usr/bin/env python3
"""Screenshot the iter04 hero mocks (M1-M4) at desktop light."""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "_site"
OUT  = Path(__file__).resolve().parent / "screenshots" / "iter04_mocks"
OUT.mkdir(parents=True, exist_ok=True)

MOCKS = [
    ("m1_polaroid",  f"file://{SITE}/explore-m1.html"),
    ("m2_strip",     f"file://{SITE}/explore-m2.html"),
    ("m3_ambient",   f"file://{SITE}/explore-m3.html"),
    ("m4_horizontal",f"file://{SITE}/explore-m4.html"),
]
VIEWPORT = {"width": 1440, "height": 900}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = ctx.new_page()
        for slug, url in MOCKS:
            out = OUT / f"iter04_{slug}.png"
            try:
                page.goto(url, wait_until="networkidle", timeout=20000)
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
