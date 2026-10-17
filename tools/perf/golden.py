"""Fingerprint simulator output for fixed seeds, to check that a speed-up
changes no result. ``python tools/perf/golden.py > before.txt`` on the old
code, then again on the new code, and diff. Prints run time per case."""

import hashlib
import json
import time

import numpy as np

from neuralmind.research.single import run_single
from neuralmind.world import World2D, WorldConfig

FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate"}


def world_digest(cfg, ticks):
    w = World2D(WorldConfig(**cfg, max_ticks=ticks))
    w.reset()
    for _ in range(ticks):
        w.step(learning=True)
    h = hashlib.sha256()
    for ag in w.agents:
        h.update(np.asarray(ag.pos).tobytes())
        h.update(np.float64(ag.energy).tobytes())
        for cn in ag._plastic:
            h.update(cn.weights.tobytes())
    h.update(str(len(w.agents)).encode())
    return h.hexdigest()[:16]


CASES = {
    "solo_default": lambda: world_digest({"seed": 3}, 300),
    "solo_full": lambda: world_digest({**FULL, "seed": 4}, 300),
    "social12_full": lambda: world_digest({**FULL, "seed": 5, "social": True, "n_agents": 12, "n_food": 24}, 120),
    "evolve_social": lambda: world_digest({"seed": 6, "social": True, "evolve": True}, 600),
    "evolve_blind_hearing": lambda: world_digest({"seed": 7, "social": True, "evolve": True, "directional_hearing": True,
                                                  "critic": "state", "credit_chosen_only": True}, 300),
    "run_single_social": lambda: hashlib.sha256(json.dumps(run_single(
        {**FULL, "seed": 8, "social": True, "n_agents": 4, "max_ticks": 60}, 2, 2, 50), sort_keys=True).encode()).hexdigest()[:16],
}

if __name__ == "__main__":
    for name, f in CASES.items():
        t = time.perf_counter()
        d = f()
        print(f"{name:22s} {d}  {time.perf_counter() - t:6.2f}s", flush=True)
