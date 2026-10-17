"""Exploratory: does the frustration->attack drive cancel the learning gain of social agents?

Trains a 12-agent social group without hazards (all learning, 1500 ticks), then
tests agent 0 frozen among frozen peers on held-out worlds, untrained and
trained, with the drive on, off for agent 0 only, or off for the whole group.
Reports food, attack rate, times attacked and mean frustration. Not pre-registered.
"""

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.world import World2D, WorldConfig

CFG = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate",
       "n_hazard": 0, "max_ticks": 500, "n_agents": 12, "n_food": 24, "social": True}
WORLDS = range(9800, 9804)


def test(w, seed, keep, drive_off):
    w.reset(seed=seed, keep_weights=keep)
    for ag in w.agents[:1] if drive_off == "self" else w.agents if drive_off == "all" else []:
        ag.aggr_gain = 0.0
    ag = w.agents[0]
    att = ag.actions.index("attack")
    hits = t = 0
    fr = []
    for _ in range(500):
        if not ag.alive:
            break
        w.step(learning=False)
        hits += ag.last_action == att
        fr.append(ag.affect.frustration)
        t += 1
    return [ag.food_eaten, hits / max(1, t), ag.attacked, float(np.mean(fr))]


def job(seed):
    cfg = {**CFG, "n_agents": int(sys.argv[2]) if len(sys.argv) > 2 else 12}
    w = World2D(WorldConfig(**cfg, seed=seed))
    for ep in range(3):
        w.reset(keep_weights=ep > 0)
        w.run(learning=True)
    out = {}
    for mode in ("on", "self", "all"):
        out[f"trained/{mode}"] = np.mean([test(w, s, True, mode) for s in WORLDS], axis=0)
        out[f"untrained/{mode}"] = np.mean([test(World2D(WorldConfig(**cfg, seed=s)), s, False, mode)
                                            for s in WORLDS], axis=0)
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    with ProcessPoolExecutor(max_workers=7) as ex:
        res = list(ex.map(job, range(870, 870 + n)))
    for k in res[0]:
        v = np.array([r[k] for r in res])
        print(f"{k:16s} food {v[:, 0].mean():5.1f}  attack {v[:, 1].mean():.3f}  attacked {v[:, 2].mean():5.1f}  frustration {v[:, 3].mean():.3f}")
    for mode in ("on", "self", "all"):
        g = np.array([r[f"trained/{mode}"][0] - r[f"untrained/{mode}"][0] for r in res])
        print(f"gain drive {mode:4s}: {g.mean():+.2f}  per seed {np.round(g, 1)}")
