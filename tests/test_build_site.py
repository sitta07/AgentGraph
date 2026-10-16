"""The static-site build: what the browser gets, checked without a browser."""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_site  # noqa: E402


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("site") / "site"
    build_site.build(out)
    return out


def test_pages_load_static_mode_before_common_js(site):
    for page in ("index.html", "lab.html"):
        html = (site / page).read_text()
        assert html.index("static/static-mode.js") < html.index("static/common.js")
    for f in ("app.js", "lab.js", "common.js", "pyodide-worker.js", "assets/kenney/tiny_town.png"):
        assert (site / "static" / f).is_file()


def test_engine_zip_has_no_server_code_and_runs_from_the_zip(site):
    zp = site / "static" / "neuralmind.zip"
    names = set(zipfile.ZipFile(zp).namelist())
    assert "neuralmind/playground.py" in names and "neuralmind/world.py" in names
    assert not names & {"neuralmind/server.py", "neuralmind/lab.py"}
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import json; "
            "from neuralmind import playground as p; assert p.__file__.startswith(sys.argv[1]); "
            "s = p.Session(); p.dispatch(s, '/api/session', '{}'); "
            "print(p.dispatch(s, '/api/step', json.dumps({'n': 3}))[0])")
    out = subprocess.run([sys.executable, "-I", "-c", code, str(zp)],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "200"


def test_lab_data_matches_the_server_and_charts_are_copied(site):
    from neuralmind import lab
    studies = json.loads((site / "data/lab/studies.json").read_text())["studies"]
    assert [s["id"] for s in studies] == [s["id"] for s in lab.studies()["studies"]]
    for s in studies:
        for chart in s["charts"]:
            assert (site / "results" / s["folder"] / chart).is_file()
        if s["has_report"]:
            assert json.loads((site / f"data/lab/reports/{s['folder']}.json").read_text())["markdown"]
    specs = json.loads((site / "data/lab/specs.json").read_text())["specs"]
    assert len(specs) == len(lab.specs()["specs"])
