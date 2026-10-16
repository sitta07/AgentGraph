"""Exploratory: how much training does a W 'full' single agent need before learning pays?

Trains one agent for a total of T ticks (in episodes of at most 500 ticks),
then tests it frozen on 500-tick held-out worlds. Not pre-registered.
"""

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.research.single import _test
from neuralmind.world import World2D, WorldConfig

FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True}
BUDGETS = (150, 500, 1500, 5000, 20000)


def job(args):
    seed, budget = args
    ep = min(500, budget)
    w = World2D(WorldConfig(**FULL, seed=seed, max_ticks=ep))
    for i in range(budget // ep):
        w.reset(keep_weights=i > 0)
        w.run(learning=True)
    w.cfg.max_ticks = 500
    seeds = range(9500, 9508)
    trained, _ = _test(w, seeds, False)
    naive, _ = _test(w, seeds, False, {**FULL, "max_ticks": 500})
    return seed, budget, trained, naive


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    jobs = [(s, b) for b in BUDGETS for s in range(700, 700 + n)]
    with ProcessPoolExecutor(max_workers=4) as ex:
        out = list(ex.map(job, jobs))
    for b in BUDGETS:
        rows = [r for r in out if r[1] == b]
        t = np.array([r[2] for r in rows]); u = np.array([r[3] for r in rows])
        print(f"budget {b:6d} ticks  trained {t.mean():5.2f}  untrained {u.mean():5.2f}  "
              f"gain {np.mean(t - u):+5.2f}  per-seed {np.round(t, 1)}", flush=True)
