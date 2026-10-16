"""Build the static, install-free site (GitHub Pages) into ``site/``.

    python tools/build_site.py            # then: python -m http.server -d site

The Playground runs the real engine in the browser: pyodide-worker.js loads
Pyodide + NumPy from a CDN and the ``neuralmind`` package from
``static/neuralmind.zip``, and answers every Playground ``/api/*`` call with
:func:`neuralmind.playground.dispatch`. The Discovery Lab reads the committed
studies, specs and reports, precomputed here into ``data/lab/*.json`` with the
same functions the local server uses. Needs FastAPI installed (it imports
:mod:`neuralmind.lab`).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from neuralmind import lab  # noqa: E402

WEBUI = ROOT / "neuralmind" / "webui"
# Server-only modules: they import FastAPI and are never called in the browser.
NOT_IN_BROWSER = {"neuralmind/server.py", "neuralmind/lab.py"}
COMMON_JS = '<script src="static/common.js"></script>'


def package_zip(dest: Path) -> int:
    """Zip the importable ``neuralmind`` package (Python files only), byte-stable."""
    files = sorted(p for p in (ROOT / "neuralmind").rglob("*.py")
                   if "__pycache__" not in p.parts and "webui" not in p.parts
                   and p.relative_to(ROOT).as_posix() not in NOT_IN_BROWSER)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
    return len(files)


def page(src: Path, dest: Path) -> None:
    html = src.read_text()
    if html.count(COMMON_JS) != 1:
        raise SystemExit(f"{src.name}: expected one {COMMON_JS}")
    dest.write_text(html.replace(
        COMMON_JS, '<script src="static/static-mode.js"></script>\n' + COMMON_JS))


def committed_at(path: Path) -> str | None:
    """Date of the last commit touching ``path``; checkout mtimes mean nothing in CI."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d %H:%M",
                              "--", str(path)], cwd=ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def lab_data(out: Path) -> int:
    data = out / "data" / "lab"
    (data / "reports").mkdir(parents=True)
    studies = lab.studies()
    for card in studies["studies"]:
        card["modified"] = committed_at(lab.RESULTS / card["folder"] / "results.json") or card["modified"]
    (data / "studies.json").write_text(json.dumps(studies))
    (data / "specs.json").write_text(json.dumps(lab.specs()))
    for folder in sorted({c["folder"] for c in studies["studies"]}):
        src = lab.RESULTS / folder
        if (src / "REPORT.md").exists():
            (data / "reports" / f"{folder}.json").write_text(json.dumps(lab.report(folder)))
        charts = [p for p in src.iterdir() if p.suffix in (".svg", ".png")]
        if charts:
            (out / "results" / folder).mkdir(parents=True)
            for p in charts:
                shutil.copy2(p, out / "results" / folder / p.name)
    return len(studies["studies"])


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(WEBUI, out / "static", ignore=shutil.ignore_patterns("*.html", "__pycache__"))
    for name in ("index.html", "lab.html"):
        page(WEBUI / name, out / name)
    n_py = package_zip(out / "static" / "neuralmind.zip")
    n_studies = lab_data(out)
    (out / ".nojekyll").write_text("")
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"built {out}: {n_py} Python files in neuralmind.zip, {n_studies} studies, "
          f"{size / 1e6:.1f} MB")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=ROOT / "site")
    build(ap.parse_args(argv).out.resolve())


if __name__ == "__main__":
    main()
