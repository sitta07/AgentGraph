"""Exploratory: does learning raise social agents' attack rate through the attack
neurons' own input weights, or through the movement neurons'?

Social group of 12, no hazards, 1500 training ticks, agent 0 tested frozen
among frozen peers. Variants freeze the input weights of the social actions or
of the movement actions (frozen_inputs). Not pre-registered; spent seeds.
"""

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.research.single import run_single

BASE = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate",
        "n_agents": 12, "n_food": 24, "n_hazard": 0, "social": True, "max_ticks": 500}
CONDS = {
    "learn_all": {},
    "freeze_social": {"frozen_inputs": ("attack", "share", "signal")},
    "freeze_moves": {"frozen_inputs": ("left", "forward", "right")},
}


def job(args):
    name, seed = args
    return name, run_single({**BASE, **CONDS[name], "seed": seed}, 0, 4, 9800, train_ticks=1500)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(job, [(c, s) for c in CONDS for s in range(870, 870 + n)]))
    for c in CONDS:
        rs = [r for k, r in res if k == c]
        print(c, {k: round(float(np.mean([r[k] for r in rs])), 3) for k in
                  ("learning_gain", "trained_food", "untrained_food", "trained_attack_frac",
                   "untrained_attack_frac", "trained_forward_frac")})
