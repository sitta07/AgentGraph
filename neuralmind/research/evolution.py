"""Experiment C — does selfish lifetime learning undermine kin-selected helping?

Background
----------
Kin selection predicts that costly helping can evolve when helpers mostly meet
relatives (Hamilton 1964). In viscous populations, where offspring stay near
their parents, neighbours are kin. But relatives also compete for the same
local resources, and in the simplest models the two effects cancel exactly
(Taylor 1992; West, Pen & Griffin 2002). The cancellation breaks down under
overlapping generations or elastic, density-dependent competition
(Hitchcock & Gardner 2022). Both conditions hold in this world.

Separately, lifetime learning can speed up or redirect evolution (the Baldwin
effect; Hinton & Nowlan 1987). Here the learning signal is selfish: sharing
costs the giver energy and earns no reward (r_prosocial = 0). So plasticity
should *unlearn* any innate helping. We have not found prior work that
measures this tension in agents whose behaviour comes from spiking networks
with reward-modulated plasticity.

Pre-registered hypotheses (2 x 2 design: viscous {yes, no} x learning {on, off})
-------------------------------------------------------------------------------
H5  The innate share drive (genome weight into the 'share' population,
    relative to the locomotion populations) evolves higher in viscous than in
    well-mixed populations (learning off).
    Falsified if viscous <= well-mixed (95% CI of the difference includes or
    lies below 0).
H6  In viscous populations, the realised share rate is lower with learning on
    than off.
    Falsified if on >= off.
H7  (expected null) Shares are not directed at kin more than chance. Agents
    have no kin-recognition sensor, so the fraction of shares that go to kin
    (relatedness >= 0.25) should equal the fraction of encounters that are with
    kin.

Run:
    python -m neuralmind.research.evolution --seeds 6 --ticks 6000
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from neuralmind import __version__
from neuralmind.research.stats import g_test_p, mean_ci, mutual_information, paired_diff
from neuralmind.world import World2D, WorldConfig

# Ecology chosen in a pilot so populations persist without hitting extinction:
# richer food, cheaper reproduction. substeps=4 halves compute per tick.
BASE = dict(social=True, evolve=True, r_prosocial=0.0, share_benefit=2.0,
            n_agents=12, max_pop=36, substeps=4, n_food=24, food_energy=0.6,
            repro_threshold=1.1, repro_cost=0.45)


def share_gene(ag) -> float:
    """Innate share drive: mean genome weight into 'share' / into locomotion."""
    w = ag.genome["w"]
    loco = np.mean([w[a].mean() for a in ("left", "forward", "right")])
    return float(w["share"].mean() / max(1e-9, loco))


def run_evolution(cfg_kw: dict, ticks: int, learning: bool, window: float = 0.25,
                  sample_every: int = 100) -> dict:
    """Run one evolving population; return time series + final-window metrics."""
    w = World2D(WorldConfig(**{**BASE, "max_ticks": ticks + 1, **cfg_kw}))
    start_final = int(ticks * (1 - window))
    acts, alive_ticks = Counter(), 0
    enc_ticks, enc_kin = 0, 0
    share_events, share_kin = 0, 0
    series = {"t": [], "pop": [], "share_gene": [], "aggr_gene": [],
              "generation": [], "share_rate": [], "attack_rate": []}
    win = Counter(); win_ticks = 0
    # communication: does signalling carry information about the signaller's
    # state, and does hearing a signal change what the listener does?
    tab = {k: np.zeros((2, 2)) for k in ("food", "threat", "hunger")}
    heard_action = np.zeros((2, 6))
    for t in range(ticks):
        frame = w.step(learning=learning)
        live = [a for a in w.agents if a.alive]
        if not live:
            break
        names = {a["id"]: a["action_name"] for a in frame["agents"] if a["alive"]}
        for a in live:
            nm = names.get(a.id)
            if nm is None:
                continue
            win[nm] += 1; win_ticks += 1
            if t >= start_final:
                acts[nm] += 1; alive_ticks += 1
        if t >= start_final:
            # kin structure of encounters (pairs within reach) vs of shares
            pos = np.array([a.pos for a in live])
            for i, a in enumerate(live):
                d = np.linalg.norm(pos - a.pos, axis=1)
                near = [live[j] for j in np.nonzero((d <= w.cfg.attack_radius) & (d > 0))[0]]
                if near:
                    enc_ticks += 1
                    o = min(near, key=lambda b: np.linalg.norm(b.pos - a.pos))
                    enc_kin += w.relatedness(a, o) >= 0.25
            for a in live:
                sv = getattr(a, "last_sensors", None)
                nm = names.get(a.id)
                if sv is None or nm is None or len(sv) < 11:
                    continue
                sig = int(nm == "signal")
                tab["food"][sig, int(sv[0:3].sum() > 0.2)] += 1
                tab["threat"][sig, int(sv[3:6].sum() > 0.2)] += 1
                tab["hunger"][sig, int(sv[6] > 0.5)] += 1
                heard_action[int(sv[10] > 0), a.actions.index(nm)] += 1
            byid = {a.id: a for a in w.agents}
            for e in frame["events"]:
                if e["type"] == "share" and e["src"] in byid and e["dst"] in byid:
                    share_events += 1
                    share_kin += w.relatedness(byid[e["src"]], byid[e["dst"]]) >= 0.25
        if t % sample_every == 0:
            series["t"].append(t)
            series["pop"].append(len(live))
            series["share_gene"].append(float(np.mean([share_gene(a) for a in live])))
            series["aggr_gene"].append(float(np.mean([a.aggr_gain for a in live])))
            series["generation"].append(float(np.mean([a.generation for a in live])))
            n = max(1, win_ticks)
            series["share_rate"].append(win["share"] / n)
            series["attack_rate"].append(win["attack"] / n)
            win = Counter(); win_ticks = 0
    live = [a for a in w.agents if a.alive]
    n = max(1, alive_ticks)
    return {
        "extinct": not live,
        "ticks_run": t + 1,
        "final_pop": len(live),
        "max_generation": max([a.generation for a in live] or [0]),
        "share_gene": float(np.mean([share_gene(a) for a in live])) if live else float("nan"),
        "aggr_gene": float(np.mean([a.aggr_gain for a in live])) if live else float("nan"),
        "share_rate": acts["share"] / n if alive_ticks else float("nan"),
        "attack_rate": acts["attack"] / n if alive_ticks else float("nan"),
        "share_to_kin": share_kin / share_events if share_events else float("nan"),
        "encounter_kin": enc_kin / enc_ticks if enc_ticks else float("nan"),
        "share_events": share_events,
        "signals_in_window": int(sum(t_[1].sum() for t_ in tab.values()) / 3),
        **{f"mi_signal_{k}": mutual_information(v) for k, v in tab.items()},
        **{f"p_signal_{k}": g_test_p(v) for k, v in tab.items()},
        "mi_heard_action": mutual_information(heard_action),
        "p_heard_action": g_test_p(heard_action),
        "births": w.births,
        "series": series,
    }


def _job(args):
    cfg_kw, ticks, learning = args
    return run_evolution(cfg_kw, ticks, learning)


METRICS = ("share_gene", "aggr_gene", "share_rate", "attack_rate", "share_to_kin",
           "encounter_kin", "final_pop", "max_generation")


def run_conditions(conditions: dict, seeds: int, ticks: int) -> dict:
    """Generic multi-seed runner. ``conditions`` maps a name to
    ``(world_config_overrides, learning)``. Seeds are shared across conditions
    so differences can be analysed as paired."""
    jobs, keys = [], []
    for name, (over, learn) in conditions.items():
        for s in range(seeds):
            jobs.append(({"seed": s, **over}, ticks, learn))
            keys.append((name, s))
    workers = max(1, (os.cpu_count() or 2) - 1)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        out = list(ex.map(_job, jobs))
    raw = {n: [r for (k, _), r in zip(keys, out) if k == n] for n in conditions}
    summ = {n: {m: mean_ci([r[m] for r in raw[n]]) for m in METRICS} for n in conditions}
    for n in conditions:
        summ[n]["extinctions"] = sum(r["extinct"] for r in raw[n])
    return {"raw": raw, "summary": summ}


def scarcity_aggression(seeds: int = 6, ticks: int = 6000) -> dict:
    """Experiment D — H8: the heritable aggression gene evolves higher when
    food is scarce. Falsified if scarce <= abundant (paired 95% CI)."""
    conds = {"scarce": ({"n_food": 12, "viscous": True}, True),
             "abundant": ({"n_food": 32, "viscous": True}, True)}
    res = run_conditions(conds, seeds, ticks)
    col = lambda n, m: [r[m] for r in res["raw"][n]]
    h8 = paired_diff(col("scarce", "aggr_gene"), col("abundant", "aggr_gene"))
    att = paired_diff(col("scarce", "attack_rate"), col("abundant", "attack_rate"))
    res.update({"experiment": "scarcity_aggression", "version": __version__,
                "design": {"seeds": seeds, "ticks": ticks, "base": BASE,
                           "conditions": {k: v[0] for k, v in conds.items()}},
                "tests": {"H8_scarce_minus_abundant_aggr_gene": h8,
                          "scarce_minus_abundant_attack_rate": att},
                "verdict": {"H8_supported": bool(h8["lo"] > 0)}})
    return res


CONDITIONS = {
    "viscous_learn": (True, True), "viscous_nolearn": (True, False),
    "mixed_learn": (False, True), "mixed_nolearn": (False, False),
}


def experiment(seeds: int, ticks: int, extra: dict | None = None) -> dict:
    jobs, keys = [], []
    for name, (visc, learn) in CONDITIONS.items():
        for s in range(seeds):
            jobs.append(({"seed": s, "viscous": visc, **(extra or {})}, ticks, learn))
            keys.append((name, s))
    workers = max(1, (os.cpu_count() or 2) - 1)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        out = list(ex.map(_job, jobs))
    raw = {n: [r for (k, _), r in zip(keys, out) if k == n] for n in CONDITIONS}
    col = lambda n, m: [r[m] for r in raw[n]]
    summ = {n: {m: mean_ci(col(n, m)) for m in
                ("share_gene", "aggr_gene", "share_rate", "attack_rate",
                 "share_to_kin", "encounter_kin", "final_pop", "max_generation")}
            for n in CONDITIONS}
    for n in CONDITIONS:
        summ[n]["extinctions"] = sum(r["extinct"] for r in raw[n])
    h5 = paired_diff(col("viscous_nolearn", "share_gene"), col("mixed_nolearn", "share_gene"))
    h6 = paired_diff(col("viscous_nolearn", "share_rate"), col("viscous_learn", "share_rate"))
    h7 = paired_diff(col("viscous_learn", "share_to_kin") + col("viscous_nolearn", "share_to_kin"),
                     col("viscous_learn", "encounter_kin") + col("viscous_nolearn", "encounter_kin"))
    return {
        "experiment": "selfish_learning_vs_kin_helping",
        "version": __version__,
        "design": {"seeds": seeds, "ticks": ticks, "base": BASE, "extra": extra or {},
                   "conditions": {k: {"viscous": v, "learning": l}
                                  for k, (v, l) in CONDITIONS.items()}},
        "summary": summ,
        "tests": {"H5_viscous_minus_mixed_share_gene": h5,
                  "H6_nolearn_minus_learn_share_rate(viscous)": h6,
                  "H7_share_to_kin_minus_encounter_kin(viscous)": h7},
        "verdict": {"H5_supported": bool(h5["lo"] > 0),
                    "H6_supported": bool(h6["lo"] > 0),
                    "H7_null_retained": bool(h7["lo"] <= 0 <= h7["hi"])},
        "raw": raw,
    }


def line_svg(raw: dict, metric: str, title: str) -> str:
    """Mean time series per condition as a small SVG line chart."""
    palette = ["#2a6fdb", "#7aa7f0", "#d9622b", "#f0a57a", "#3c9a5f", "#9a59c4"]
    cols = {n: palette[i % len(palette)] for i, n in enumerate(raw)}
    W, H, L, B, T = 560, 240, 50, 30, 30
    series = {}
    for n, runs in raw.items():
        L_ = min(len(r["series"]["t"]) for r in runs if r["series"]["t"]) if runs else 0
        if not L_:
            continue
        arr = np.array([r["series"][metric][:L_] for r in runs if len(r["series"]["t"]) >= L_])
        series[n] = (runs[0]["series"]["t"][:L_], np.nanmean(arr, axis=0))
    allv = np.concatenate([v for _, v in series.values()]) if series else np.array([0, 1])
    lo, hi = float(np.nanmin(allv)), float(np.nanmax(allv))
    hi = hi if hi > lo else lo + 1
    tmax = max((ts[-1] for ts, _ in series.values()), default=1) or 1
    X = lambda t: L + (W - L - 10) * t / tmax
    Y = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<text x="10" y="18" font-size="13" font-weight="bold" fill="#1a1d24">{title}</text>',
         f'<line x1="{L}" y1="{H - B}" x2="{W - 10}" y2="{H - B}" stroke="#ccd"/>',
         f'<text x="{L - 4}" y="{T + 4}" text-anchor="end" fill="#667">{hi:.3g}</text>',
         f'<text x="{L - 4}" y="{H - B}" text-anchor="end" fill="#667">{lo:.3g}</text>',
         f'<text x="{W - 10}" y="{H - 8}" text-anchor="end" fill="#667">tick {tmax}</text>']
    ly = T
    for n, (ts, v) in series.items():
        pts = " ".join(f"{X(t):.1f},{Y(x):.1f}" for t, x in zip(ts, v) if np.isfinite(x))
        o.append(f'<polyline fill="none" stroke="{cols[n]}" stroke-width="2" points="{pts}"/>')
        o.append(f'<text x="{W - 150}" y="{ly}" fill="{cols[n]}">— {n}</text>'); ly += 14
    o.append("</svg>")
    return "\n".join(o)


def write_report(res: dict, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    f = lambda c, pct=False: (f"{100 * c['mean']:.2f}% [{100 * c['lo']:.2f}, {100 * c['hi']:.2f}]" if pct
                              else f"{c['mean']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}]")
    for m, t in (("share_gene", "Innate share drive (genome)"), ("share_rate", "Share rate"),
                 ("aggr_gene", "Heritable aggression gain"), ("pop", "Population")):
        (out / f"series_{m}.svg").write_text(line_svg(res["raw"], m, t))
    s = res["summary"]
    L = ["# Experiment C — selfish learning vs kin-selected helping", "",
         f"NeuralMind {res['version']} · {time.strftime('%Y-%m-%d %H:%M')} · "
         "mean [95% bootstrap CI] over seeds, final 25% of each run.", "",
         f"Design: `{json.dumps(res['design'])}`", "",
         "| condition | innate share drive | share rate | share→kin | encounters with kin | aggression gene | final pop | max gen | extinct |",
         "|---|---|---|---|---|---|---|---|---|"]
    for n in CONDITIONS:
        c = s[n]
        L.append(f"| {n} | {f(c['share_gene'])} | {f(c['share_rate'], True)} | {f(c['share_to_kin'], True)} | "
                 f"{f(c['encounter_kin'], True)} | {f(c['aggr_gene'])} | {c['final_pop']['mean']:.1f} | "
                 f"{c['max_generation']['mean']:.1f} | {c['extinctions']} |")
    t = res["tests"]
    L += ["", "![](series_share_gene.svg) ![](series_share_rate.svg)",
          "![](series_aggr_gene.svg) ![](series_pop.svg)", "",
          "## Pre-registered tests", "",
          f"- **H5** viscous − mixed innate share drive (learning off): {f(t['H5_viscous_minus_mixed_share_gene'])} → "
          f"supported = **{res['verdict']['H5_supported']}**",
          f"- **H6** learning off − on share rate (viscous): {f(t['H6_nolearn_minus_learn_share_rate(viscous)'], True)} → "
          f"supported = **{res['verdict']['H6_supported']}**",
          f"- **H7** share→kin − encounter-kin (viscous): {f(t['H7_share_to_kin_minus_encounter_kin(viscous)'], True)} → "
          f"null retained = **{res['verdict']['H7_null_retained']}**", "",
          "A hypothesis counts as supported only if its 95% CI excludes 0 in the predicted direction."]
    p = out / "REPORT.md"
    p.write_text("\n".join(L))
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float))
    return p


def write_generic_report(res: dict, out: Path, title: str) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    f = lambda c: f"{c['mean']:.4f} [{c['lo']:.4f}, {c['hi']:.4f}]"
    for m, t in (("aggr_gene", "Heritable aggression gain"), ("attack_rate", "Attack rate"),
                 ("share_gene", "Innate share drive"), ("pop", "Population")):
        (out / f"series_{m}.svg").write_text(line_svg(res["raw"], m, t))
    L = [f"# {title}", "", f"NeuralMind {res['version']} · {time.strftime('%Y-%m-%d %H:%M')} · "
         "mean [95% bootstrap CI] over seeds, final 25% of each run.", "",
         f"Design: `{json.dumps(res['design'])}`", "",
         "| condition | " + " | ".join(METRICS) + " | extinct |",
         "|---|" + "---|" * (len(METRICS) + 1)]
    for n, c in res["summary"].items():
        L.append(f"| {n} | " + " | ".join(f(c[m]) for m in METRICS) + f" | {c['extinctions']} |")
    L += ["", "![](series_aggr_gene.svg) ![](series_attack_rate.svg)",
          "![](series_share_gene.svg) ![](series_pop.svg)", "", "## Tests", ""]
    L += [f"- {k}: {f(v)}" for k, v in res["tests"].items()]
    L += ["", f"Verdict: `{res['verdict']}` (supported only if the 95% CI excludes 0 "
              "in the predicted direction)."]
    p = out / "REPORT.md"
    p.write_text("\n".join(L))
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float))
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", choices=["kin", "scarcity"], default="kin")
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--ticks", type=int, default=6000)
    ap.add_argument("--out", default="results/evolution_kin")
    ap.add_argument("--set", nargs="*", default=[], help="extra WorldConfig overrides k=v")
    a = ap.parse_args(argv)
    extra = {}
    for kv in a.set:
        k, v = kv.split("=")
        extra[k] = (v.lower() == "true") if v.lower() in ("true", "false") else float(v) if "." in v else int(v)
    t0 = time.perf_counter()
    if a.experiment == "scarcity":
        res = scarcity_aggression(a.seeds, a.ticks)
        p = write_generic_report(res, Path(a.out), "Experiment D — does aggression evolve under scarcity?")
    else:
        res = experiment(a.seeds, a.ticks, extra)
        p = write_report(res, Path(a.out))
    print(res["verdict"], f"-> {p} ({time.perf_counter() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
