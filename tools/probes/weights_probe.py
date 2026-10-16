import sys
sys.path.insert(0, sys.argv[1])
import numpy as np
from neuralmind.world import World2D, WorldConfig
from neuralmind.research.evolution import BASE
for seed in (9000, 9001):
    w = World2D(WorldConfig(**{**BASE, "seed": seed, "viscous": True, "max_ticks": 8001}))
    for _ in range(8000):
        w.step(learning=False)
    live = [a for a in w.agents if a.alive]
    g = np.mean([a.genome["w"]["forward"] for a in live], axis=0).mean(axis=0)
    l = np.mean([a.genome["w"]["left"] for a in live], axis=0).mean(axis=0)
    r = np.mean([a.genome["w"]["right"] for a in live], axis=0).mean(axis=0)
    print(seed, len(live), "gen", np.mean([a.generation for a in live]).round(1))
    names = ["foodL","foodC","foodR","hazL","hazC","hazR","hunger","othL","othC","othR","heard"]
    for nm, row in (("forward", g), ("left", l), ("right", r)):
        print(" ", nm, " ".join(f"{n}={v:.2f}" for n, v in zip(names, row)))
