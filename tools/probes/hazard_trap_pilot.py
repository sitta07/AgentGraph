"""Exploratory: does a lone social agent fail to learn because it gets stuck in hazards?

Compares lone non-social and lone social agents with and without hazards
(W 'full' dynamics, 1500 training ticks). Not pre-registered.
"""

import sys
from concurrent.futures import ProcessPoolExecutor

from neuralmind.research.single import run_single

FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate"}
CONDS = {
    "solo": {**FULL},
    "social_alone": {**FULL, "social": True},
    "solo_nohazard": {**FULL, "n_hazard": 0},
    "social_alone_nohazard": {**FULL, "social": True, "n_hazard": 0},
}


def job(args):
    name, seed = args
    return name, seed, run_single({**CONDS[name], "seed": seed, "max_ticks": 500}, 0, 6, 9600, train_ticks=1500)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with ProcessPoolExecutor(max_workers=4) as ex:
        for name, seed, r in ex.map(job, [(c, s) for c in CONDS for s in range(740, 740 + n)]):
            print(name, seed, {k: round(r[k], 2) for k in ("trained_food", "untrained_food", "learning_gain")}, flush=True)
