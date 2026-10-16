import sys
sys.path.insert(0, sys.argv[1])
import numpy as np
from neuralmind.world import World2D, WorldConfig

def braitenberg(cfg, rng, boost):
    base = np.clip(rng.normal(cfg.w_init, cfg.w_init * 0.2, size=(cfg.n_action, 7)), 0, cfg.w_max)
    w = {a: base.copy() for a in ("left", "forward", "right")}
    for a, food_i, haz_i in (("left", 0, 2), ("forward", 1, None), ("right", 2, 0)):
        w[a][:, food_i] = np.clip(w[a][:, food_i] + boost, 0, cfg.w_max)
        if haz_i is not None:
            w[a][:, 3 + haz_i] = np.clip(w[a][:, 3 + haz_i] + boost, 0, cfg.w_max)
    return {"w": w}

def episode(seed, boost, scramble, extra):
    cfg = WorldConfig(seed=seed, scramble_senses=scramble, max_ticks=500, **extra)
    w = World2D(cfg)
    if boost is not None:
        w.agents[0].build_net(np.random.default_rng(seed + 1), genome=braitenberg(cfg, np.random.default_rng(seed + 1), boost))
    return w.run(learning=False)["food_eaten"]

for label, extra in (("default", {}), ("sparse", {"n_food": 3, "food_energy": 0.9})):
    for name, boost in (("random", None), ("braitenberg+1.5", 1.5), ("braitenberg+2.8", 2.8)):
        r = [episode(s, boost, False, extra) for s in range(9000, 9016)]
        z = [episode(s, boost, True, extra) for s in range(9000, 9016)]
        print(label, name, "real %.2f" % np.mean(r), "scrambled %.2f" % np.mean(z))
