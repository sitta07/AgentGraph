"""Exploratory: does a W 'full' learner still gain when it trains among other learners?

Uses run_single with a social multi-agent world: all agents learn during
training; agent 0 is tested frozen among its frozen peers. Not pre-registered.
"""

import sys
from concurrent.futures import ProcessPoolExecutor

from neuralmind.research.single import run_single

FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate"}
CONDS = {
    "solo": {**FULL},
    "social12": {**FULL, "social": True, "n_agents": 12, "n_food": 24},
}


def job(args):
    name, seed = args
    r = run_single({**CONDS[name], "seed": seed, "max_ticks": 500}, 0, 6, 9600, train_ticks=1500)
    return name, seed, r


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with ProcessPoolExecutor(max_workers=4) as ex:
        for name, seed, r in ex.map(job, [(c, s) for c in CONDS for s in range(720, 720 + n)]):
            print(name, seed, {k: round(r[k], 2) for k in ("trained_food", "trained_food_scrambled",
                  "untrained_food", "learning_gain")}, flush=True)
