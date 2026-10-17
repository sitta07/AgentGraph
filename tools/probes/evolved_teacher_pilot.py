"""Exploratory: does evolution reshape the learning reward (the "teacher")?
Unregistered seeds; used to choose run length before pre-registration."""

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.research.evolution import run_evolution

FIX = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate"}
CONDS = {
    "designer": ({**FIX}, True),
    "evolved_designer": ({**FIX, "evolve_teacher": True}, True),
    "evolved_scratch": ({**FIX, "evolve_teacher": True, "teacher_init": (0.0, 0.0, 0.0, 0.0)}, True),
    "drift_nolearn": ({**FIX, "evolve_teacher": True}, False),
}
KEYS = ("food_rate", "survival_ticks", "attack_rate", "max_generation", "final_pop",
        "teacher_align", "teacher_approach", "teacher_energy", "teacher_hunger")


def job(args):
    name, seed, ticks = args
    cfg, learning = CONDS[name]
    r = run_evolution({**cfg, "seed": seed}, ticks, learning)
    return name, {k: r.get(k, float("nan")) for k in KEYS}


if __name__ == "__main__":
    n, ticks = int(sys.argv[1]), int(sys.argv[2])
    with ProcessPoolExecutor(max_workers=7) as ex:
        res = list(ex.map(job, [(c, s, ticks) for c in CONDS for s in range(9550, 9550 + n)]))
    for c in CONDS:
        rs = [r for k, r in res if k == c]
        print(f"{c:17s}", {k: round(float(np.nanmean([r[k] for r in rs])), 3) for k in KEYS}, flush=True)
