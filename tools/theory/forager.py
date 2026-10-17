"""Independent replication of the shaping bias, outside NeuralMind.

A point agent forages for eight food items in the unit square with a linear
softmax policy over four actions: left, forward, right and stay (stay does
not move, like NeuralMind's social actions). Features are three egocentric
food bins (the same bin formula as NeuralMind) and a bias. Learning is
per-step, with credit given by (r - b) times an eligibility:

  hebb:  e = outer(pi, x)               Hebbian, non-negative post activity
  score: e = outer(onehot(a) - pi, x)   score function (policy gradient)

Reward: +1 for eating, plus 4 x (change in alignment with the nearest food)
when shaping is on (0 on eating steps); eaten food reappears at random. Baseline b: one running mean
("scalar") or one running mean per binarised food-bin state ("state").
No NeuralMind code is used.
"""

from __future__ import annotations

import math
import sys

import numpy as np

SPEED, TURN, EAT, RANGE, N_FOOD = 0.02, 0.3, 0.05, 0.5, 8


def bins(pos, heading, food):
    sig = np.zeros(3)
    for f in food:
        dv = f - pos
        dist = math.hypot(dv[0], dv[1])
        if 1e-9 < dist <= RANGE:
            bearing = math.atan2(dv[1], dv[0])
            prox = 1.0 - dist / RANGE
            for k, off in enumerate((0.9, 0.0, -0.9)):
                a = math.cos(bearing - (heading + off))
                if a > 0:
                    sig[k] += a * a * prox
    return np.clip(sig, 0.0, 1.0)


def align(pos, heading, food):
    f = food[int(np.argmin(np.linalg.norm(food - pos, axis=1)))]
    return math.cos(math.atan2(f[1] - pos[1], f[0] - pos[0]) - heading)


def step(pos, heading, a):
    if a == 3:
        return pos, heading
    heading += TURN if a == 0 else -TURN if a == 2 else 0.0
    sp = SPEED * (1.0 if a == 1 else 0.5)
    p = pos + sp * np.array([math.cos(heading), math.sin(heading)])
    if not 0 <= p[0] <= 1:
        heading = math.pi - heading
    if not 0 <= p[1] <= 1:
        heading = -heading
    return np.clip(p, 0.0, 1.0), heading % (2 * math.pi)


def run(seed: int, rule: str, baseline: str, shaping: bool, train: int = 30000, test: int = 5000,
        lr: float = 0.05) -> dict:
    rng = np.random.default_rng(seed)
    W = rng.normal(0.0, 0.1, (4, 4))
    b_scalar, b_state = 0.0, np.zeros(8)
    pos, heading, food = rng.uniform(0.1, 0.9, 2), rng.uniform(0, 2 * math.pi), rng.uniform(0.05, 0.95, (N_FOOD, 2))
    eaten = stays = 0
    for t in range(train + test):
        learn = t < train
        s = bins(pos, heading, food)
        x = np.append(s, 1.0)
        z = W @ x
        pi = np.exp(z - z.max()); pi /= pi.sum()
        a = int(rng.choice(4, p=pi))
        al0 = align(pos, heading, food)
        pos, heading = step(pos, heading, a)
        r = 0.0
        hit = np.nonzero(np.linalg.norm(food - pos, axis=1) < EAT)[0]
        if hit.size:
            r = float(hit.size)
            food[hit] = rng.uniform(0.05, 0.95, (hit.size, 2))
            eaten += (not learn) * hit.size
        elif shaping:
            r = 4.0 * (align(pos, heading, food) - al0)
        stays += (not learn) and a == 3
        if learn:
            key = int((s > 0.2) @ np.array([1, 2, 4]))
            b = b_scalar if baseline == "scalar" else b_state[key]
            post = pi if rule == "hebb" else np.eye(4)[a] - pi
            W += lr * (r - b) * np.outer(post, x)
            b_scalar += 0.05 * (r - b_scalar)
            b_state[key] += 0.05 * (r - b_state[key])
    return {"food_per_1000": 1000.0 * eaten / test, "stay_frac": stays / test,
            "w_food_forward": float(W[1, :3].sum()), "w_food_stay": float(W[3, :3].sum())}


CONDITIONS = {
    "hebb_scalar": ("hebb", "scalar", True),
    "hebb_state": ("hebb", "state", True),
    "hebb_noshape": ("hebb", "scalar", False),
    "score_scalar": ("score", "scalar", True),
    "score_state": ("score", "state", True),
    "score_noshape": ("score", "scalar", False),
}

def _job(args):
    name, seed = args
    rule, baseline, shaping = CONDITIONS[name]
    return name, seed, run(seed, rule, baseline, shaping)


if __name__ == "__main__":
    import json
    from concurrent.futures import ProcessPoolExecutor
    start, n, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    jobs = [(name, s) for name in CONDITIONS for s in range(start, start + n)]
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(_job, jobs))
    raw = {name: [r for k, _, r in rows if k == name] for name in CONDITIONS}
    with open(out, "w") as f:
        json.dump({"seeds": [start, start + n], "raw": raw}, f, indent=1)
    for name, rs in raw.items():
        print(name, {k: round(float(np.mean([r[k] for r in rs])), 3) for k in rs[0]})
