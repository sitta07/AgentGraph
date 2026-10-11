"""Record README media (GIFs/PNGs) from the running app.

Every frame is a capture of real simulation state rendered by the app. Nothing
is drawn by this script.

    python -m neuralmind.server &            # serve on 127.0.0.1:8000
    python tools/make_media.py                # writes docs/media/*

Dev-only dependencies: playwright (Apache-2.0, uses the locally installed
Google Chrome via channel="chrome") and Pillow.
"""

from __future__ import annotations

import io
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parents[1] / "docs" / "media"


def to_gif(frames: list[bytes], path: Path, width: int, ms: int, colors: int = 96) -> None:
    imgs = []
    for b in frames:
        im = Image.open(io.BytesIO(b)).convert("RGB")
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
        imgs.append(im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                dither=Image.Dither.NONE))
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=ms, loop=0,
                 optimize=True, disposal=2)
    print(f"{path.name}: {len(imgs)} frames, {path.stat().st_size / 1e6:.2f} MB")


def capture(page, selector: str, n: int, every: float) -> list[bytes]:
    el = page.locator(selector)
    frames = []
    for _ in range(n):
        frames.append(el.screenshot(type="png"))
        time.sleep(every)
    return frames


def setup_world(page, agents: int, food: int, social: bool, evolve: bool) -> None:
    page.goto(URL)
    page.wait_for_function("window.S && S.session")
    page.evaluate(f"""() => {{
        const set = (id, v) => {{ const e = document.getElementById(id); e.value = v;
                                  e.dispatchEvent(new Event('input')); }};
        set('c_n_agents', {agents}); set('c_n_food', {food}); set('speed', 30);
        document.getElementById('t_social').checked = {str(social).lower()};
        document.getElementById('t_evolve').checked = {str(evolve).lower()};
        document.getElementById('btnNew').click();
    }}""")
    page.wait_for_timeout(1200)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 900}, device_scale_factor=1)

        # 1. Evolving social population: births, attacks, shares, signals, moods.
        setup_world(page, agents=8, food=22, social=True, evolve=True)
        page.click("#btnPlay")
        page.wait_for_timeout(6000)                 # let the population grow first
        to_gif(capture(page, "#world", n=60, every=0.12), OUT / "evolution_world.gif", 440, 110, colors=48)
        page.click("#btnPlay")

        # 2. Brain scanner of one individual + its action competition.
        page.wait_for_timeout(300)
        page.click("#btnPlay")
        to_gif(capture(page, ".col >> nth=0 >> .panel >> nth=0", n=45, every=0.12),
               OUT / "brain_scanner.gif", 340, 110)
        page.click("#btnPlay")

        # 3. Whole playground (static).
        page.evaluate("() => document.querySelectorAll('.col').forEach(c => c.scrollTop = 0)")
        page.screenshot(path=str(OUT / "playground.png"))

        # 4. Discovery Lab (static).
        page.goto(URL + "/lab")
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "discovery_lab.png"), full_page=False)
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
