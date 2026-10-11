"""Social-behaviour experiments for spiking-neural agents.

Pre-registered questions (fixed before the runs; results are reported whatever
they turn out to be):

Experiment A — Deprivation and aggression (pathway ablation)
    H1  Removing all food (deprivation) increases the per-agent attack rate.
    H2  That increase is smaller when the frustration->attack pathway is
        ablated (aggression_gain = 0), i.e. the effect is mediated by it.
    Design: 5 agents, social on, `fed` phase then `deprived` phase, same seeds
    in both conditions (paired). Metric: attacks per alive agent-tick.

Experiment B — Scarcity x kinship
    H3  Scarcer food (fewer items) increases the attack rate.
    H4  Sharing increases when kinship makes it pay (r * benefit > 1) versus
        a selfish population (r = 0).
    Design: grid of n_food x r_prosocial, several seeds per cell, learning on.

Nothing here hard-codes an outcome: every action is chosen by each agent's own
spiking network, and the numbers are whatever the simulation produces.

Run:
    python -m neuralmind.research.social all --seeds 10
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
from neuralmind.research.stats import gini, mean_ci, paired_diff
from neuralmind.world import World2D, WorldConfig

ACTION_NAMES = ("left", "forward", "right", "attack", "share", "signal")


# ----------------------------------------------------------------- simulate
def simulate(cfg_kw: dict, ticks: int, deprive_at: int | None = None,
             learning: bool = True) -> dict:
    """Run one population and return phase-wise behavioural metrics."""
    cfg = WorldConfig(**{"social": True, "max_ticks": ticks + 1, **cfg_kw})
    w = World2D(cfg)
    phases = {"pre": Counter(), "post": Counter()}
    alive_ticks = {"pre": 0, "post": 0}
    frustration = {"pre": [], "post": []}
    # encounter-conditioned counts: ticks with another agent within reach
    enc = {"pre": Counter(), "post": Counter()}
    enc_ticks = {"pre": 0, "post": 0}
    death_tick = {ag.id: None for ag in w.agents}
    deaths_by_attack = 0
    for t in range(ticks):
        if deprive_at is not None and t == deprive_at:
            w.set_deprive(True)
        phase = "post" if (deprive_at is not None and t >= deprive_at) else "pre"
        frame = w.step(learning=learning)
        live = [a for a in frame["agents"] if a["alive"]]
        for a in frame["agents"]:
            if a["alive"]:
                phases[phase][a["action_name"]] += 1
                alive_ticks[phase] += 1
                frustration[phase].append(a["affect"]["frustration"])
                near = any(o is not a and np.hypot(o["agent"][0] - a["agent"][0],
                           o["agent"][1] - a["agent"][1]) <= cfg.attack_radius for o in live)
                if near:
                    enc_ticks[phase] += 1
                    enc[phase][a["action_name"]] += 1
            elif death_tick[a["id"]] is None:
                death_tick[a["id"]] = t
        deaths_by_attack += sum(1 for e in frame["events"] if e["type"] == "death")
        if not any(ag.alive for ag in w.agents):
            break

    def rates(ph):
        n = max(1, alive_ticks[ph])
        return {k: phases[ph][k] / n for k in ACTION_NAMES}

    def enc_rates(ph):
        n = enc_ticks[ph]
        return {k: (enc[ph][k] / n if n else float("nan")) for k in ACTION_NAMES}

    survival = [death_tick[i] if death_tick[i] is not None else ticks for i in death_tick]
    return {
        "rates_pre": rates("pre"), "rates_post": rates("post"),
        "enc_rates_pre": enc_rates("pre"), "enc_rates_post": enc_rates("post"),
        "encounter_share_pre": enc_ticks["pre"] / max(1, alive_ticks["pre"]),
        "encounter_share_post": enc_ticks["post"] / max(1, alive_ticks["post"]),
        "alive_ticks_pre": alive_ticks["pre"], "alive_ticks_post": alive_ticks["post"],
        "frustration_pre": float(np.mean(frustration["pre"])) if frustration["pre"] else 0.0,
        "frustration_post": float(np.mean(frustration["post"])) if frustration["post"] else 0.0,
        "food_eaten": int(sum(ag.food_eaten for ag in w.agents)),
        "mean_survival": float(np.mean(survival)),
        "deaths_by_attack": deaths_by_attack,
        "energy_gini_end": gini([max(0.0, ag.energy) for ag in w.agents]),
        "attacks": int(sum(ag.attacks for ag in w.agents)),
        "shares": int(sum(ag.shares_given for ag in w.agents)),
        "signals": int(sum(ag.signals for ag in w.agents)),
    }


def _job(args):
    cfg_kw, ticks, deprive_at, learning = args
    return simulate(cfg_kw, ticks, deprive_at, learning)


def _parallel(jobs: list) -> list:
    workers = max(1, (os.cpu_count() or 2) - 1)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_job, jobs))


# ------------------------------------------------------------ experiment A
def deprivation_aggression(seeds: int = 10, ticks: int = 300, deprive_at: int = 150,
                           n_agents: int = 5) -> dict:
    conditions = {"intact": (1.0, True), "ablated": (0.0, True),
                  "intact_v1": (1.0, False), "ablated_v1": (0.0, False)}
    jobs, keys = [], []
    for name, (gain, primary) in conditions.items():
        for s in range(seeds):
            jobs.append(({"seed": s, "n_agents": n_agents, "aggression_gain": gain,
                          "affect_from_primary": primary}, ticks, deprive_at, True))
            keys.append((name, s))
    out = _parallel(jobs)
    raw = {name: [r for (n, _), r in zip(keys, out) if n == name] for name in conditions}

    summary = {}
    for name, runs in raw.items():
        pre = [r["rates_pre"]["attack"] for r in runs]
        post = [r["rates_post"]["attack"] for r in runs]
        summary[name] = {
            "attack_rate_fed": mean_ci(pre),
            "attack_rate_deprived": mean_ci(post),
            "deprivation_effect": paired_diff(post, pre),
            "frustration_fed": mean_ci([r["frustration_pre"] for r in runs]),
            "frustration_deprived": mean_ci([r["frustration_post"] for r in runs]),
            "attack_given_encounter_fed": mean_ci([r["enc_rates_pre"]["attack"] for r in runs]),
            "attack_given_encounter_deprived": mean_ci([r["enc_rates_post"]["attack"] for r in runs]),
            "encounter_share_fed": mean_ci([r["encounter_share_pre"] for r in runs]),
            "encounter_share_deprived": mean_ci([r["encounter_share_post"] for r in runs]),
        }
    eff_i = [r["rates_post"]["attack"] - r["rates_pre"]["attack"] for r in raw["intact"]]
    eff_a = [r["rates_post"]["attack"] - r["rates_pre"]["attack"] for r in raw["ablated"]]
    summary["mediation"] = paired_diff(eff_i, eff_a)  # same seeds -> paired
    h1 = summary["intact"]["deprivation_effect"]["lo"] > 0
    h2 = summary["mediation"]["lo"] > 0
    return {
        "experiment": "deprivation_aggression",
        "design": {"seeds": seeds, "ticks": ticks, "deprive_at": deprive_at,
                   "n_agents": n_agents,
                   "conditions": {k: {"aggression_gain": g, "affect_from_primary": p}
                                  for k, (g, p) in conditions.items()}},
        "summary": summary,
        "verdict": {"H1_deprivation_increases_attacks": bool(h1),
                    "H2_effect_mediated_by_frustration_pathway": bool(h2)},
        "raw": raw,
    }


# ------------------------------------------------------------ experiment B
def scarcity_kinship(seeds: int = 8, ticks: int = 400, food_levels=(2, 4, 8, 16),
                     r_levels=(0.0, 0.5, 1.0), n_agents: int = 5) -> dict:
    jobs, keys = [], []
    for nf in food_levels:
        for r in r_levels:
            for s in range(seeds):
                jobs.append(({"seed": s, "n_agents": n_agents, "n_food": nf,
                              "r_prosocial": r}, ticks, None, True))
                keys.append((nf, r, s))
    out = _parallel(jobs)
    cells = {}
    for (nf, r, s), res in zip(keys, out):
        cells.setdefault(f"{nf}|{r}", []).append(res)
    grid = {}
    for k, runs in cells.items():
        grid[k] = {
            "attack_rate": mean_ci([x["rates_pre"]["attack"] for x in runs]),
            "share_rate": mean_ci([x["rates_pre"]["share"] for x in runs]),
            "signal_rate": mean_ci([x["rates_pre"]["signal"] for x in runs]),
            "survival": mean_ci([x["mean_survival"] for x in runs]),
            "food_per_agent": mean_ci([x["food_eaten"] / n_agents for x in runs]),
            "energy_gini": mean_ci([x["energy_gini_end"] for x in runs]),
            "encounter_share": mean_ci([x["encounter_share_pre"] for x in runs]),
            "attack_given_encounter": mean_ci([x["enc_rates_pre"]["attack"] for x in runs]),
            "share_given_encounter": mean_ci([x["enc_rates_pre"]["share"] for x in runs]),
        }
    lo_f, hi_f = min(food_levels), max(food_levels)
    att = lambda nf: [x["rates_pre"]["attack"] for r in r_levels for x in cells[f"{nf}|{r}"]]
    shr = lambda r: [x["rates_pre"]["share"] for nf in food_levels for x in cells[f"{nf}|{r}"]]
    scarcity_effect = paired_diff(att(lo_f), att(hi_f))
    kin_effect = paired_diff(shr(max(r_levels)), shr(min(r_levels)))
    enc = lambda nf: [x["encounter_share_pre"] for r in r_levels for x in cells[f"{nf}|{r}"]]
    attE = lambda nf: [x["enc_rates_pre"]["attack"] for r in r_levels for x in cells[f"{nf}|{r}"]]
    shrE = lambda r: [x["enc_rates_pre"]["share"] for nf in food_levels for x in cells[f"{nf}|{r}"]]
    density_effect = paired_diff(enc(hi_f), enc(lo_f))
    scarcity_effect_enc = paired_diff(attE(lo_f), attE(hi_f))
    kin_effect_enc = paired_diff(shrE(max(r_levels)), shrE(min(r_levels)))
    return {
        "experiment": "scarcity_kinship",
        "design": {"seeds": seeds, "ticks": ticks, "food_levels": list(food_levels),
                   "r_levels": list(r_levels), "n_agents": n_agents},
        "grid": grid,
        "effects": {"scarcity_on_attack(scarce - abundant)": scarcity_effect,
                    "kinship_on_share(r_max - r_min)": kin_effect,
                    "abundance_on_encounters(abundant - scarce)": density_effect,
                    "scarcity_on_attack_given_encounter": scarcity_effect_enc,
                    "kinship_on_share_given_encounter": kin_effect_enc},
        "verdict": {"H3_scarcity_increases_attacks": bool(scarcity_effect["lo"] > 0),
                    "H4_kinship_increases_sharing": bool(kin_effect["lo"] > 0)},
    }


# ------------------------------------------------------------------ output
def _fmt(ci: dict, pct: bool = True) -> str:
    f = (lambda v: f"{100 * v:.2f}%") if pct else (lambda v: f"{v:.2f}")
    return f"{f(ci['mean'])} [{f(ci['lo'])}, {f(ci['hi'])}]"


def heatmap_svg(grid: dict, rows, cols, metric: str, title: str, pct=True) -> str:
    vals = [grid[f"{r}|{c}"][metric]["mean"] for r in rows for c in cols]
    vmax = max(vals) or 1.0
    cw, ch, lx, ty = 92, 40, 90, 46
    W, H = lx + cw * len(cols) + 10, ty + ch * len(rows) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'font-family="sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<text x="10" y="20" font-size="14" font-weight="bold" fill="#1a1d24">{title}</text>',
           f'<text x="{lx}" y="38" fill="#5b6472">kinship r →</text>']
    for j, c in enumerate(cols):
        out.append(f'<text x="{lx + j * cw + cw / 2}" y="{ty - 4 + 0}" text-anchor="middle" '
                   f'fill="#1a1d24" dy="-2">{c}</text>')
    for i, r in enumerate(rows):
        out.append(f'<text x="{lx - 8}" y="{ty + i * ch + ch / 2 + 4}" text-anchor="end" '
                   f'fill="#1a1d24">{r} food</text>')
        for j, c in enumerate(cols):
            v = grid[f"{r}|{c}"][metric]["mean"]
            t = v / vmax
            col = (int(239 - t * (239 - 47)), int(244 - t * (244 - 95)), int(255 - t * (255 - 190)))
            txt = "#ffffff" if t > 0.55 else "#1a1d24"
            label = f"{100 * v:.1f}%" if pct else f"{v:.1f}"
            out.append(f'<rect x="{lx + j * cw}" y="{ty + i * ch}" width="{cw - 2}" '
                       f'height="{ch - 2}" rx="4" fill="rgb{col}"/>')
            out.append(f'<text x="{lx + j * cw + cw / 2 - 1}" y="{ty + i * ch + ch / 2 + 4}" '
                       f'text-anchor="middle" fill="{txt}">{label}</text>')
    out.append(f'<text x="10" y="{H - 10}" fill="#5b6472">mean over seeds; darker = higher</text>')
    out.append("</svg>")
    return "\n".join(out)


def write_report(results: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Social-behaviour experiments — results", "",
             f"NeuralMind {__version__} · generated {time.strftime('%Y-%m-%d %H:%M')} · "
             "values are mean [95% bootstrap CI] over seeds.", ""]
    A = results.get("deprivation_aggression")
    if A:
        s = A["summary"]
        lines += ["## A. Does food deprivation make agents more aggressive?", "",
                  f"Design: {A['design']}", "",
                  "| condition | attack rate (fed) | attack rate (deprived) | change | frustration fed → deprived |",
                  "|---|---|---|---|---|"]
        for c in ("intact", "ablated", "intact_v1", "ablated_v1"):
            lines.append(f"| {c} | {_fmt(s[c]['attack_rate_fed'])} | {_fmt(s[c]['attack_rate_deprived'])} | "
                         f"{_fmt(s[c]['deprivation_effect'])} | "
                         f"{s[c]['frustration_fed']['mean']:.2f} → {s[c]['frustration_deprived']['mean']:.2f} |")
        lines += ["", "Encounter-conditioned (only ticks with another agent within reach):", "",
                  "| condition | encounters (fed → deprived) | attack \\| encounter (fed) | attack \\| encounter (deprived) |",
                  "|---|---|---|---|"]
        for c in ("intact", "ablated"):
            lines.append(f"| {c} | {_fmt(s[c]['encounter_share_fed'])} → {_fmt(s[c]['encounter_share_deprived'])} | "
                         f"{_fmt(s[c]['attack_given_encounter_fed'])} | {_fmt(s[c]['attack_given_encounter_deprived'])} |")
        lines += ["", "`_v1` rows use the pilot model where shaping noise also drove affect "
                      "(`affect_from_primary=False`); kept for transparency."]
        lines += ["", f"Mediation (intact effect − ablated effect): {_fmt(s['mediation'])}", "",
                  f"Verdict: H1 = **{A['verdict']['H1_deprivation_increases_attacks']}**, "
                  f"H2 = **{A['verdict']['H2_effect_mediated_by_frustration_pathway']}** "
                  "(true only if the 95% CI excludes zero).", ""]
    B = results.get("scarcity_kinship")
    if B:
        rows, cols, g = B["design"]["food_levels"], B["design"]["r_levels"], B["grid"]
        for metric, title, pct in (("attack_rate", "Attack rate", True),
                                   ("share_rate", "Share rate", True),
                                   ("survival", "Mean survival (ticks)", False)):
            (out_dir / f"heatmap_{metric}.svg").write_text(
                heatmap_svg(g, rows, cols, metric, title, pct))
        lines += ["## B. Scarcity × kinship", "", f"Design: {B['design']}", "",
                  "![attack](heatmap_attack_rate.svg) ![share](heatmap_share_rate.svg) "
                  "![survival](heatmap_survival.svg)", "",
                  "| food | r | attack rate | share rate | signal rate | encounters | attack \\| enc | share \\| enc | survival | food/agent |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for nf in rows:
            for r in cols:
                c = g[f"{nf}|{r}"]
                lines.append(f"| {nf} | {r} | {_fmt(c['attack_rate'])} | {_fmt(c['share_rate'])} | "
                             f"{_fmt(c['signal_rate'])} | {_fmt(c['encounter_share'])} | "
                             f"{_fmt(c['attack_given_encounter'])} | {_fmt(c['share_given_encounter'])} | "
                             f"{_fmt(c['survival'], False)} | "
                             f"{_fmt(c['food_per_agent'], False)} |")
        e = B["effects"]
        lines += ["", f"Scarcity effect on attacks (scarcest − most abundant): "
                      f"{_fmt(e['scarcity_on_attack(scarce - abundant)'])}",
                  f"Kinship effect on sharing (highest r − r=0): {_fmt(e['kinship_on_share(r_max - r_min)'])}",
                  f"Abundance effect on encounter rate (abundant − scarce): {_fmt(e['abundance_on_encounters(abundant - scarce)'])}",
                  f"Scarcity effect on attack | encounter: {_fmt(e['scarcity_on_attack_given_encounter'])}",
                  f"Kinship effect on share | encounter: {_fmt(e['kinship_on_share_given_encounter'])}", "",
                  f"Verdict: H3 = **{B['verdict']['H3_scarcity_increases_attacks']}**, "
                  f"H4 = **{B['verdict']['H4_kinship_increases_sharing']}**.", ""]
    lines += ["## Caveats", "",
              "- Rates are per alive agent-tick; behaviour is chosen by each agent's spiking network.",
              "- Within-lifetime learning only (no evolution); small populations (5 agents).",
              "- The frustration→attack coupling is a modelling hypothesis, not established biology.",
              "- A 'False' verdict means the data did not support the hypothesis at 95% — it is reported, not hidden."]
    p = out_dir / "REPORT.md"
    p.write_text("\n".join(lines))
    (out_dir / "results.json").write_text(json.dumps(results, indent=1))
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("which", choices=["deprivation", "grid", "all"])
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--out", default="results/social")
    a = ap.parse_args(argv)
    results, t0 = {}, time.perf_counter()
    if a.which in ("deprivation", "all"):
        results["deprivation_aggression"] = deprivation_aggression(seeds=a.seeds)
        print("A done", results["deprivation_aggression"]["verdict"])
    if a.which in ("grid", "all"):
        results["scarcity_kinship"] = scarcity_kinship(seeds=max(2, a.seeds))
        print("B done", results["scarcity_kinship"]["verdict"])
    p = write_report(results, Path(a.out))
    print(f"report -> {p}  ({time.perf_counter() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
