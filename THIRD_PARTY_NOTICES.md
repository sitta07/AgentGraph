# Third-Party Notices

NeuralMind is distributed under the MIT License (see `LICENSE`). It bundles
**no third-party source code**; it does bundle the CC0 art assets listed below. This file records the external projects
it depends on at runtime/dev time, and projects studied for reference whose
licenses would govern any future integration.

## Runtime / development dependencies (installed via pip, not vendored)

| Project | Version pin | License | Use |
|---|---|---|---|
| NumPy | see `requirements-neuralmind.txt` | BSD-3-Clause | All numerical arrays/RNG in the simulation core |
| pytest | dev only | MIT | Test runner |

These are permissively licensed and are **not** redistributed as part of this
repository; users install them themselves.

## Reference-only projects (studied, NOT integrated or copied)

The following were researched (documentation/metadata) to inform the design but
**no code from them is included** in this repository. If any is integrated in
the future (e.g. as an optional engine adapter, see ADR-0004), its license below
governs that use and this notice must be updated accordingly.

| Project | License | Repository |
|---|---|---|
| The Virtual Brain (tvb-root) | GPL-3.0-or-later (some bundled parts differ) | https://github.com/the-virtual-brain/tvb-root |
| Brian2 | CeCILL 2.1 | https://github.com/brian-team/brian2 |
| NEST simulator | GPL-2.0-or-later (some bundled MIT/LGPL parts) | https://github.com/nest/nest-simulator |
| FlyBrainLab | License not confirmed at time of writing — verify before any use | https://github.com/FlyBrainLab/FlyBrainLab |

> Note on copyleft: TVB, Brian2, and NEST are copyleft. They may be used as
> **optional, separately-installed dependencies**. Their source must **not** be
> copied into this MIT-licensed repository. See
> `docs/architecture/ARCHITECTURE_DECISIONS.md` (ADR-0002, ADR-0004).

## Bundled art assets (CC0)

| Asset | Author | License | Location | Use |
|---|---|---|---|---|
| [Tiny Town 1.1](https://kenney.nl/assets/tiny-town) (tilemap_packed.png) | [Kenney](https://kenney.nl) | CC0 1.0 | `neuralmind/webui/assets/kenney/tiny_town.png` | grass, tree border, mushroom (food) tiles |
| [Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) (tilemap_packed.png) | [Kenney](https://kenney.nl) | CC0 1.0 | `neuralmind/webui/assets/kenney/tiny_dungeon.png` | people sprites, spike/fire hazard tiles, gravestone |

The original `License.txt` files are kept next to the images. CC0 requires no
attribution; we credit Kenney anyway: here, in the README, and in the footer
of both web pages.

## Web backend dependencies (optional, pip-installed, not vendored)

| Project | License | Use |
|---|---|---|
| FastAPI | MIT | Playground HTTP API |
| Uvicorn | BSD-3-Clause | ASGI server |
| httpx | BSD-3-Clause | Test client only |
| PettingZoo | MIT | optional multi-agent RL interface (`neuralmind/envs`) |
| Gymnasium | MIT | observation/action spaces for the PettingZoo wrapper |
| Playwright (Python) | Apache-2.0 | dev-only: records README media (`tools/make_media.py`) |
| Pillow | MIT-CMU | dev-only: assembles GIFs |

## Browser build (GitHub Pages; loaded from a CDN at runtime, not vendored)

| Project | Version pin | License | Use |
|---|---|---|---|
| [Pyodide](https://pyodide.org) | 0.29.5, from `cdn.jsdelivr.net/pyodide/v0.29.5/full/` | MPL-2.0 (bundled CPython: PSF) | Runs the Python engine in the browser via WebAssembly (`neuralmind/webui/pyodide-worker.js`) |
| NumPy (Pyodide build) | 2.2.5, shipped with Pyodide 0.29.5 | BSD-3-Clause | Same as above, inside the browser |

`tools/build_site.py` writes no third-party code into `site/`; the visitor's
browser downloads Pyodide and NumPy directly from the CDN. Pyodide is MPL-2.0,
a file-level copyleft licence: using it unmodified this way places no
conditions on NeuralMind's own MIT code.
