import sys
sys.path.insert(0, sys.argv[1])
import numpy as np
from multiprocessing import Pool
from neuralmind.world import World2D, WorldConfig
SUB = int(sys.argv[2]); RESET = sys.argv[3] == "1"; CRITIC = sys.argv[4]; NORM = sys.argv[5] == "1"

def job(train_seed):
    w = World2D(WorldConfig(seed=train_seed, reset_each_decision=RESET, substeps=SUB, critic=CRITIC, normalize=NORM))
    for ep in range(40):
        w.reset(keep_weights=ep > 0); w.run(learning=True)
    r = {}
    for scr in (False, True):
        w.cfg.scramble_senses = scr
        f = []
        for s in range(9000, 9016):
            w.reset(seed=s, keep_weights=True); f.append(w.run(learning=False)["food_eaten"])
        r["scr" if scr else "real"] = float(np.mean(f))
    return train_seed, r

if __name__ == "__main__":
    with Pool(3) as p:
        res = p.map(job, range(500, 512))
    for s, r in res: print(s, r)
    real = np.array([r["real"] for _, r in res]); scr = np.array([r["scr"] for _, r in res])
    print(f"SUB={SUB} reset={RESET} critic={CRITIC} normalize={NORM} trained real {real.mean():.2f} scrambled {scr.mean():.2f} real>scr {int((real>scr).sum())}/12 median diff {np.median(real-scr):.2f}")
