import sys
sys.path.insert(0, sys.argv[1])
import numpy as np
from multiprocessing import Pool
from neuralmind.world import World2D, WorldConfig

def job(train_seed):
    w = World2D(WorldConfig(seed=train_seed))
    for ep in range(40):
        w.reset(keep_weights=ep > 0); w.run(learning=True)
    out = {"trained_sighted": [], "trained_scr": [], "naive_sighted": [], "naive_scr": []}
    for s in range(9000, 9016):
        for scr in (False, True):
            w.cfg.scramble_senses = scr
            w.reset(seed=s, keep_weights=True)
            out["trained_scr" if scr else "trained_sighted"].append(w.run(learning=False)["food_eaten"])
            n = World2D(WorldConfig(seed=s, scramble_senses=scr))
            out["naive_scr" if scr else "naive_sighted"].append(n.run(learning=False)["food_eaten"])
    return train_seed, {k: float(np.mean(v)) for k, v in out.items()}

if __name__ == "__main__":
    with Pool(3) as p:
        for s, r in p.map(job, range(500, 506)):
            print(s, {k: round(v, 2) for k, v in r.items()})
