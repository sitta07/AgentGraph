import sys, time
sys.path.insert(0, sys.argv[1])
import numpy as np
from multiprocessing import Pool
from neuralmind.research.evolution import run_evolution
FIX = {"substeps": 32, "reset_each_decision": True, "normalize": True}

def job(a):
    name, over, learning, seed = a
    t0 = time.time()
    r = run_evolution({"seed": seed, **over}, 3000, learning)
    return name, seed, round(time.time() - t0), {k: round(r[k], 4) for k in ("food_rate", "extinct01", "final_pop", "attack_rate", "sense_gain", "innate_foraging_sighted")}

if __name__ == "__main__":
    jobs = [(n, o, l, s) for s in (9200, 9201) for n, o, l in (
        ("fixed_learn", FIX, True), ("fixed_nolearn", FIX, False), ("default_learn", {}, True), ("default_nolearn", {}, False))]
    with Pool(2) as p:
        for r in p.map(job, jobs):
            print(*r)
