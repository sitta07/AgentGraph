"""Exploratory: does approach shaping (instead of alignment shaping) let
social agents learn in groups? Spent seeds, not pre-registered."""

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.research.single import run_single

FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate",
        "n_hazard": 0, "max_ticks": 500}
CONDS = {
    "solo_align": {**FULL},
    "solo_approach": {**FULL, "reward_mode": "approach"},
    "social12_align": {**FULL, "social": True, "n_agents": 12, "n_food": 24},
    "social12_approach": {**FULL, "social": True, "n_agents": 12, "n_food": 24, "reward_mode": "approach"},
}


def job(args):
    name, seed = args
    return name, run_single({**CONDS[name], "seed": seed}, 0, 3, 9800, train_ticks=1500)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with ProcessPoolExecutor(max_workers=3) as ex:
        res = list(ex.map(job, [(c, s) for c in CONDS for s in range(870, 870 + n)]))
    for c in CONDS:
        rs = [r for k, r in res if k == c]
        print(f"{c:18s}", {k: round(float(np.mean([r[k] for r in rs])), 3) for k in
              ("learning_gain", "trained_food", "untrained_food", "sense_gain", "trained_attack_frac", "untrained_attack_frac")},
              "per seed", [round(r["learning_gain"], 1) for r in rs], flush=True)
