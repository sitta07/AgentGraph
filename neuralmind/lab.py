"""Discovery Lab backend: browse committed studies and launch replications.

Every study in ``results/<name>/`` (a ``results.json`` written by
:mod:`neuralmind.research`) is normalised into cards that list the
experiment's hypotheses, test statistics with CIs, verdicts and charts. New
replications can be launched from the browser. They run in a background
thread and write their output to ``results/lab_<timestamp>_<kind>/``, where
it appears next to the committed studies.
"""

from __future__ import annotations

import json
import threading
import time
import traceback
from pathlib import Path

from fastapi import APIRouter, HTTPException

RESULTS = Path(__file__).resolve().parent.parent / "results"
STUDIES = Path(__file__).resolve().parent.parent / "studies"
router = APIRouter(prefix="/api/lab")

_JOBS: dict[str, dict] = {}
_LOCK = threading.Lock()

STUDY_TITLES = {
    "deprivation_aggression": "Does food deprivation make agents more aggressive?",
    "scarcity_kinship": "Scarcity × kinship: who attacks, who shares?",
    "selfish_learning_vs_kin_helping": "Does selfish lifetime learning undermine kin-selected helping?",
    "crowding_and_spatial_kin": "Crowding and spatial kin cues (follow-up)",
    "scarcity_aggression": "Does a heritable aggression gene evolve under scarcity?",
}


def _cards_from(name: str, data: dict) -> list[dict]:
    blocks = ([data] if "verdict" in data else
              [v for v in data.values() if isinstance(v, dict) and "verdict" in v])
    cards = []
    for b in blocks:
        exp = b.get("experiment", name)
        tests = b.get("tests") or b.get("effects") or {}
        if not tests and "summary" in b and "mediation" in b["summary"]:
            tests = {"mediation(intact - ablated deprivation effect)": b["summary"]["mediation"]}
        cards.append({
            "id": f"{name}/{exp}", "folder": name, "experiment": exp,
            "title": b.get("title") or STUDY_TITLES.get(exp, exp.replace("_", " ")),
            "question": b.get("question", ""),
            "preregistration": b.get("preregistration"),
            "deviations": b.get("deviations") or {},
            "design": b.get("design", {}), "verdict": b.get("verdict", {}),
            "tests": {k: v for k, v in tests.items() if isinstance(v, dict) and "mean" in v},
        })
    return cards


@router.get("/studies")
def studies():
    out = []
    if RESULTS.exists():
        for d in sorted(RESULTS.iterdir()):
            f = d / "results.json"
            if not f.exists():
                continue
            try:
                data = json.loads(f.read_text())
            except json.JSONDecodeError:
                continue
            for card in _cards_from(d.name, data):
                # the deprivation study has no charts; the heatmaps belong to the grid
                card["charts"] = ([] if card["experiment"] == "deprivation_aggression"
                                  else sorted(p.name for p in d.glob("*.svg")))
                card["has_report"] = (d / "REPORT.md").exists()
                card["modified"] = time.strftime("%Y-%m-%d %H:%M",
                                                 time.localtime(f.stat().st_mtime))
                out.append(card)
    return {"studies": out}


@router.get("/report/{folder}")
def report(folder: str):
    d = (RESULTS / folder).resolve()
    if RESULTS.resolve() not in d.parents or not (d / "REPORT.md").exists():
        raise HTTPException(404, "no such report")
    return {"markdown": (d / "REPORT.md").read_text()}


@router.get("/specs")
def specs():
    """Registered studies in studies/*.json, with whether results exist yet."""
    from neuralmind.research.spec import load, preregistration
    out = []
    for f in sorted(STUDIES.glob("*.json")) if STUDIES.exists() else []:
        try:
            sp = load(f)
        except (ValueError, json.JSONDecodeError) as e:
            out.append({"file": f.name, "error": str(e)})
            continue
        out.append({"id": sp["id"], "file": f.name, "title": sp["title"],
                    "question": sp["question"], "seeds": sp.get("seeds"),
                    "ticks": sp.get("ticks"), "hypotheses": sp["hypotheses"],
                    "conditions": list(sp["conditions"]),
                    "preregistration": preregistration(f),
                    "has_results": (RESULTS / sp["id"] / "results.json").exists()})
    return {"specs": out}


# --------------------------------------------------------------- launching
KINDS = {
    "social": "Lifetime social learning (A + B)",
    "kin": "Selfish learning vs kin helping (C)",
    "scarcity": "Aggression gene × scarcity (D)",
}


def _run(job_id: str, kind: str, seeds: int, ticks: int, spec_id: str | None = None) -> None:
    out = RESULTS / f"lab_{time.strftime('%Y%m%d_%H%M%S')}_{spec_id or kind}"
    try:
        if kind == "spec":
            from neuralmind.research import spec as sp
            path = STUDIES / f"{spec_id}.json"
            res = sp.run(sp.load(path), path, seeds, ticks)
            sp.write(res, out)
        elif kind == "social":
            from neuralmind.research import social
            res = {"deprivation_aggression": social.deprivation_aggression(seeds=seeds),
                   "scarcity_kinship": social.scarcity_kinship(seeds=max(2, seeds))}
            social.write_report(res, out)
        else:
            from neuralmind.research import evolution as ev
            if kind == "kin":
                ev.write_report(ev.experiment(seeds, ticks), out)
            else:
                ev.write_generic_report(ev.scarcity_aggression(seeds, ticks), out,
                                        "Experiment D — does aggression evolve under scarcity?")
        status, err = "done", None
    except Exception:  # surfaced to the UI, never swallowed
        status, err = "error", traceback.format_exc(limit=3)
    with _LOCK:
        _JOBS[job_id].update(status=status, error=err, folder=out.name,
                             finished=time.strftime("%H:%M:%S"))


@router.post("/run")
def run(body: dict | None = None):
    body = body or {}
    kind = body.get("kind", "kin")
    spec_id = body.get("spec")
    if kind == "spec":
        if not spec_id or not (STUDIES / f"{spec_id}.json").exists() or "/" in spec_id:
            raise HTTPException(400, "unknown spec")
    elif kind not in KINDS:
        raise HTTPException(400, f"kind must be one of {list(KINDS) + ['spec']}")
    seeds = min(max(int(body.get("seeds", 3)), 2), 20)
    ticks = min(max(int(body.get("ticks", 1500)), 200), 20000)
    with _LOCK:
        if any(j["status"] == "running" for j in _JOBS.values()):
            raise HTTPException(409, "an experiment is already running")
        job_id = f"job{len(_JOBS) + 1}"
        _JOBS[job_id] = {"id": job_id, "kind": kind, "seeds": seeds,
                         "title": f"Registered study {spec_id}" if kind == "spec" else KINDS[kind],
                         "ticks": ticks, "status": "running",
                         "started": time.strftime("%H:%M:%S")}
    threading.Thread(target=_run, args=(job_id, kind, seeds, ticks, spec_id), daemon=True).start()
    return _JOBS[job_id]


@router.get("/jobs")
def jobs():
    with _LOCK:
        return {"jobs": list(_JOBS.values()), "kinds": KINDS}
