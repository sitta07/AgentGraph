"""Exploratory: where does learning move input weight, and why do social agents attack more?

Trains agent 0 with its group (all learning) for 1500 ticks, then reports the
change in input weight from each sensor group to each action (mean over
neurons, trained - innate) and, for social groups, the attack rate when tested
frozen: untrained, trained, and trained with its frustration->attack drive off.
Not pre-registered.
"""

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.world import World2D, WorldConfig

FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate",
        "n_hazard": 0, "max_ticks": 500}
CONDS = {
    "social12": {**FULL, "n_agents": 12, "n_food": 24, "social": True},
    "crowd12": {**FULL, "n_agents": 12, "n_food": 24},
    "solo": {**FULL},
}
GROUPS = {"food": slice(0, 3), "threat": slice(3, 6), "hunger": slice(6, 7),
          "other": slice(7, 10), "heard": slice(10, 11)}


def test(w, no_drive=False):
    ag = w.agents[0]
    if no_drive:
        ag.aggr_gain = 0.0
    att = ag.actions.index("attack") if "attack" in ag.actions else -1
    hits = t = 0
    for _ in range(500):
        if not ag.alive:
            break
        w.step(learning=False)
        hits += ag.last_action == att
        t += 1
    return hits / max(1, t), ag.food_eaten


def job(args):
    name, seed = args
    cfg = CONDS[name]
    w = World2D(WorldConfig(**cfg, seed=seed))
    for ep in range(3):
        w.reset(keep_weights=ep > 0)
        w.run(learning=True)
    ag = w.agents[0]
    n = ag.n_sensors
    dw = {cn.post: {g: float((cn.weights - ag.genome["w"][cn.post])[:, s].mean())
                    for g, s in GROUPS.items() if s.start < n} for cn in ag._plastic}
    out = {}
    if cfg.get("social"):
        out["untrained"] = test(World2D(WorldConfig(**cfg, seed=9800)))
        w.reset(seed=9800, keep_weights=True)
        out["trained"] = test(w)
        w.reset(seed=9800, keep_weights=True)
        out["trained_no_drive"] = test(w, no_drive=True)
    return name, dw, out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(CONDS)
    with ProcessPoolExecutor(max_workers=7) as ex:
        res = list(ex.map(job, [(c, s) for c in names for s in range(870, 870 + n)]))
    for c in names:
        rs = [r for r in res if r[0] == c]
        print(c)
        for a in rs[0][1]:
            print(f"  {a:8s}", {g: round(float(np.mean([r[1][a][g] for r in rs])), 3) for g in rs[0][1][a]})
        for k in rs[0][2]:
            v = np.array([r[2][k] for r in rs])
            print(f"  {k:17s} attack {v[:, 0].mean():.3f}  food {v[:, 1].mean():.1f}")
