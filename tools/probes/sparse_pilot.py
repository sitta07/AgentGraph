import sys, json
sys.path.insert(0, sys.argv[1])
import numpy as np
from multiprocessing import Pool
from neuralmind.research.evolution import run_evolution

WORLDS = {"dense": {"n_food": 24, "food_energy": 0.6}, "sparse": {"n_food": 6, "food_energy": 2.4}}

def job(a):
    world, scr, learning, seed = a
    r = run_evolution({"seed": seed, **WORLDS[world], "scramble_senses": scr}, 5000, learning)
    return world, scr, learning, seed, r["food_rate"], r["extinct01"], r["sense_gain"]

if __name__ == "__main__":
    jobs = [(w, s, l, seed) for w in WORLDS for s in (False, True) for l in (False, True) for seed in range(9100, 9104)]
    with Pool(2) as p:
        res = p.map(job, jobs)
    import collections
    agg = collections.defaultdict(list)
    for w, s, l, seed, fr, ex, sg in res:
        agg[(w, "scr" if s else "real", "learn" if l else "nolearn")].append((fr, ex, sg))
    for k, v in sorted(agg.items()):
        a = np.array(v, dtype=float)
        print(k, "food_rate %.4f" % np.nanmean(a[:, 0]), "extinct %d/4" % a[:, 1].sum(), "sense_gain %.2f" % np.nanmean(a[:, 2]))
