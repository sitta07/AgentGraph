"""Declarative, pre-registered studies.

A study is a JSON file in ``studies/`` that fixes the question, the conditions,
the seeds, the metrics and the decision rule for every hypothesis. Commit the
spec **before** running it: the runner records the git commit that last
touched the spec and whether the working copy differs from it, so anyone can
check that the hypotheses predate the data.

    python -m neuralmind.research.spec studies/D_scarcity_aggression.json

Spec format::

    {
      "id": "D_scarcity_aggression",
      "title": "...", "question": "...", "background": "...",
      "simulator": "evolution",
      "seeds": 6, "ticks": 6000,
      "base": {"<WorldConfig field>": value},
      "conditions": {"name": {"config": {...}, "learning": true}},
      "hypotheses": [
        {"id": "H8", "statement": "...", "metric": "aggr_gene",
         "a": "scarce", "b": "abundant", "direction": "greater"}
      ]
    }

``direction`` sets the decision rule on the paired difference a − b (same seeds):

* ``greater``: supported if the 95% CI lower bound is above 0.
* ``less``: supported if the upper bound is below 0.
* ``none``: "no difference detected" if the CI contains 0. This is weak
  evidence and is reported as such.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from neuralmind import __version__
from neuralmind.research.evolution import line_svg, run_conditions
from neuralmind.research.stats import mean_ci, paired_diff

from neuralmind.paths import home

ROOT = home()
REQUIRED = ("id", "title", "question", "simulator", "conditions", "hypotheses")
DIRECTIONS = ("greater", "less", "none")


def load(path: str | Path) -> dict:
    spec = json.loads(Path(path).read_text())
    missing = [k for k in REQUIRED if k not in spec]
    if missing:
        raise ValueError(f"spec missing keys: {missing}")
    if spec["simulator"] != "evolution":
        raise ValueError("only simulator='evolution' is supported so far")
    for h in spec["hypotheses"]:
        for k in ("id", "statement", "metric", "a", "b", "direction"):
            if k not in h:
                raise ValueError(f"hypothesis {h.get('id', '?')} missing '{k}'")
        if h["direction"] not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}")
        for c in (h["a"], h["b"]):
            if c not in spec["conditions"]:
                raise ValueError(f"hypothesis {h['id']} refers to unknown condition '{c}'")
    return spec


def preregistration(path: Path) -> dict:
    """Git evidence that the spec existed (unchanged) before the run."""
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    rel = str(path.resolve().relative_to(ROOT)) if ROOT in path.resolve().parents else str(path)
    commit = git("log", "-1", "--format=%H %cI", "--", rel)
    dirty = bool(git("status", "--porcelain", "--", rel))
    return {"spec_path": rel, "commit": commit.split(" ")[0] if commit else None,
            "committed_at": commit.split(" ")[1] if " " in commit else None,
            "modified_since_commit": dirty,
            "preregistered": bool(commit) and not dirty}


def decide(ci: dict, direction: str) -> str:
    if not np.isfinite(ci["mean"]):
        return "no data"
    if direction == "greater":
        return "supported" if ci["lo"] > 0 else "not supported"
    if direction == "less":
        return "supported" if ci["hi"] < 0 else "not supported"
    return "no difference detected" if ci["lo"] <= 0 <= ci["hi"] else "difference detected"


def run(spec: dict, path: Path, seeds: int | None = None, ticks: int | None = None) -> dict:
    deviations = {}
    if seeds is not None and seeds != spec.get("seeds"):
        deviations["seeds"] = {"registered": spec.get("seeds"), "used": seeds}
    if ticks is not None and ticks != spec.get("ticks"):
        deviations["ticks"] = {"registered": spec.get("ticks"), "used": ticks}
    seeds = seeds or spec.get("seeds", 6)
    ticks = ticks or spec.get("ticks", 6000)
    prereg = preregistration(path)
    conds = {n: ({**spec.get("base", {}), **c.get("config", {})}, bool(c.get("learning", True)))
             for n, c in spec["conditions"].items()}
    res = run_conditions(conds, seeds, ticks)
    metrics = sorted(k for k, v in res["raw"][next(iter(conds))][0].items()
                     if isinstance(v, (int, float)) and not isinstance(v, bool))
    col = lambda n, m: [r[m] for r in res["raw"][n]]
    summary = {n: {m: mean_ci(col(n, m)) for m in metrics} for n in conds}
    tests, verdict = {}, {}
    for h in spec["hypotheses"]:
        ci = paired_diff(col(h["a"], h["metric"]), col(h["b"], h["metric"]))
        tests[f"{h['id']}: {h['metric']} ({h['a']} − {h['b']})"] = ci
        verdict[h["id"]] = decide(ci, h["direction"])
    return {"experiment": spec["id"], "title": spec["title"], "question": spec["question"],
            "background": spec.get("background", ""), "hypotheses": spec["hypotheses"],
            "version": __version__, "preregistration": prereg, "deviations": deviations,
            "design": {"seeds": seeds, "ticks": ticks, "base": spec.get("base", {}),
                       "conditions": spec["conditions"]},
            "summary": summary, "tests": tests, "verdict": verdict, "raw": res["raw"]}


def write(res: dict, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    f = lambda c: f"{c['mean']:.4g} [{c['lo']:.4g}, {c['hi']:.4g}]"
    charts = [("share_gene", "Innate share drive"), ("aggr_gene", "Heritable aggression gain"),
              ("share_rate", "Share rate"), ("attack_rate", "Attack rate"),
              ("pop", "Population"), ("generation", "Mean generation")]
    for m, t in charts:
        (out / f"series_{m}.svg").write_text(line_svg(res["raw"], m, t))
    pr = res["preregistration"]
    L = [f"# {res['title']}", "", f"**Question.** {res['question']}", ""]
    if res["background"]:
        L += [res["background"], ""]
    L += [f"NeuralMind {res['version']} · {time.strftime('%Y-%m-%d %H:%M')} · "
          "mean [95% bootstrap CI] over seeds; paired differences use the same seeds.", "",
          f"**Pre-registration:** spec `{pr['spec_path']}` at commit `{pr['commit']}` "
          f"({pr['committed_at']}) · unchanged since commit: **{not pr['modified_since_commit']}** · "
          f"preregistered: **{pr['preregistered']}**"]
    if res["deviations"]:
        L += [f"**Deviations from the registered design:** `{json.dumps(res['deviations'])}`"]
    L += ["", "## Hypotheses", "", "| id | statement | test (a − b) | result |", "|---|---|---|---|"]
    for h in res["hypotheses"]:
        key = f"{h['id']}: {h['metric']} ({h['a']} − {h['b']})"
        L.append(f"| {h['id']} | {h['statement']} | {f(res['tests'][key])} | **{res['verdict'][h['id']]}** |")
    shown = [m for m in ("innate_foraging", "share_gene", "aggr_gene", "share_rate",
                         "attack_rate", "share_given_encounter", "encounter_rate",
                         "final_pop", "max_generation") if m in next(iter(res["summary"].values()))]
    L += ["", "## Conditions", "", "| condition | " + " | ".join(shown) + " |",
          "|---|" + "---|" * len(shown)]
    for n, c in res["summary"].items():
        L.append(f"| {n} | " + " | ".join(f(c[m]) for m in shown) + " |")
    L += ["", " ".join(f"![](series_{m}.svg)" for m, _ in charts), "",
          f"Full per-metric summaries and raw per-run data: `results.json`."]
    p = out / "REPORT.md"
    p.write_text("\n".join(L))
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float))
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--seeds", type=int, help="override (recorded as a deviation)")
    ap.add_argument("--ticks", type=int, help="override (recorded as a deviation)")
    ap.add_argument("--out", help="default: results/<spec id>")
    a = ap.parse_args(argv)
    path = Path(a.spec)
    spec = load(path)
    t0 = time.perf_counter()
    res = run(spec, path, a.seeds, a.ticks)
    p = write(res, Path(a.out or ROOT / "results" / spec["id"]))
    print(res["verdict"], "preregistered:", res["preregistration"]["preregistered"],
          f"-> {p} ({time.perf_counter() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
