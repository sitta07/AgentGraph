"""Where does lifetime weight drift come from? (exploratory probe)

Every learning update changes a connection by ``lr * rpe * eligibility``. This
probe runs one evolving population and sums that product for locomotion and
for social input weights, split by the kind of tick it happened on:

* ``eat``: the primary reward was positive (food, theft or gift),
* ``pain``: the primary reward was negative (hazard, being robbed, attack cost),
* ``shaping``: no primary reward, only the shaped approach/alignment term.

    python -m neuralmind.research.drift_probe --seed 900 --ticks 3000
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from neuralmind.research.evolution import BASE
from neuralmind.world import Agent, World2D, WorldConfig

LOCO = ("left", "forward", "right")


def probe(seed: int, ticks: int, cfg: dict | None = None) -> dict:
    sums = defaultdict(float)
    counts = defaultdict(int)
    original = Agent.learn_and_affect

    def wrapped(self, reward, sensors, in_hazard, learning, hurt=False, primary=None, action=None):
        elig = {cn.post: float(cn._stdp.eligibility.sum()) for cn in self._plastic}
        rpe = original(self, reward, sensors, in_hazard, learning, hurt=hurt,
                       primary=primary, action=action)
        if learning:
            kind = "eat" if (primary or 0) > 0 else "pain" if (primary or 0) < 0 else "shaping"
            counts[kind] += 1
            counts["rpe_pos" if rpe > 0 else "rpe_neg"] += 1
            for post, e in elig.items():
                group = "loco" if post in LOCO else "social"
                sums[f"{group}_{kind}"] += self.cfg.lr * rpe * e
                sums[f"elig_{group}_{'pos' if rpe > 0 else 'neg'}"] += e
        return rpe

    Agent.learn_and_affect = wrapped
    try:
        w = World2D(WorldConfig(**{**BASE, "viscous": True, "seed": seed,
                                   "max_ticks": ticks + 1, **(cfg or {})}))
        for _ in range(ticks):
            w.step(learning=True)
            if not any(a.alive for a in w.agents):
                break
    finally:
        Agent.learn_and_affect = original
    return {"seed": seed, "ticks": ticks, "updates": dict(counts),
            "dw": {k: round(v, 4) for k, v in sorted(sums.items()) if not k.startswith("elig")},
            "eligibility": {k: round(v, 1) for k, v in sorted(sums.items()) if k.startswith("elig")}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=900)
    ap.add_argument("--ticks", type=int, default=3000)
    a = ap.parse_args(argv)
    print(json.dumps(probe(a.seed, a.ticks), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
