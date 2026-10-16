import sys, numpy as np
sys.path.insert(0, sys.argv[1])
from neuralmind.world import World2D, WorldConfig
sys.path.insert(0, sys.argv[2]); from braitenberg_pilot import braitenberg

def p_left(ag, s, rng, n=300):
    c = np.zeros(3)
    for _ in range(n):
        a, _, _ = ag.decide(s, rng); c[a] += 1
    return c / n

L = np.array([0.9, 0.2, 0, 0, 0, 0, 0.2]); R = np.array([0, 0.2, 0.9, 0, 0, 0, 0.2]); N0 = np.array([0, 0, 0, 0, 0, 0, 0.2])
for name, boost, noise in (("random", None, 3.5), ("braitenberg+2.8", 2.8, 3.5), ("random", None, 0.5), ("braitenberg+2.8", 2.8, 0.5)):
    cfg = WorldConfig(seed=1, action_noise=noise)
    w = World2D(cfg); ag = w.agents[0]
    if boost: ag.build_net(np.random.default_rng(2), genome=braitenberg(cfg, np.random.default_rng(2), boost))
    rng = np.random.default_rng(0)
    pl, pr, pn = p_left(ag, L, rng), p_left(ag, R, rng), p_left(ag, N0, rng)
    print(f"{name:16s} noise={noise}  food-left P(L,F,R)={np.round(pl,2)}  food-right={np.round(pr,2)}  nothing={np.round(pn,2)}")
