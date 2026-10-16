"""Single-agent learning studies: train one agent, then test it on held-out worlds.

Each run trains a fresh agent for ``train_episodes`` episodes (learning on,
weights kept between episodes), then freezes it and measures food eaten per
episode on ``test_worlds`` held-out world seeds, with real and with scrambled
food/hazard senses. An untrained agent with the same configuration is tested
on the same worlds as the baseline.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from neuralmind.world import World2D, WorldConfig

COLLAPSED = 1.0   # mean food per test episode below this counts as a collapsed learner


def _test(w: World2D, seeds: range, scramble: bool, untrained_cfg: dict | None = None) -> tuple[float, float]:
    food, fwd = [], []
    for s in seeds:
        if untrained_cfg is None:
            w.cfg.scramble_senses = scramble
            w.reset(seed=s, keep_weights=True)
            env = w
        else:
            env = World2D(WorldConfig(**{**untrained_cfg, "seed": s, "scramble_senses": scramble}))
        ag = env.agents[0]
        moves = 0
        for _ in range(env.cfg.max_ticks):
            if not ag.alive:
                break
            env.step(learning=False)
            moves += ag.last_action == 1
        food.append(ag.food_eaten)
        fwd.append(moves / max(1, env.t))
    return float(np.mean(food)), float(np.mean(fwd))


def run_single(cfg_kw: dict, train_episodes: int, test_worlds: int, test_seed_start: int) -> dict:
    w = World2D(WorldConfig(**cfg_kw))
    curve = []
    for ep in range(train_episodes):
        w.reset(keep_weights=ep > 0)
        curve.append(w.run(learning=True)["food_eaten"])
    seeds = range(test_seed_start, test_seed_start + test_worlds)
    base = {k: v for k, v in cfg_kw.items() if k != "seed"}
    trained, trained_fwd = _test(w, seeds, False)
    trained_scr, _ = _test(w, seeds, True)
    naive, naive_fwd = _test(w, seeds, False, base)
    naive_scr, _ = _test(w, seeds, True, base)
    q = max(1, train_episodes // 4)
    return {
        "trained_food": trained, "trained_food_scrambled": trained_scr,
        "untrained_food": naive, "untrained_food_scrambled": naive_scr,
        "learning_gain": trained - naive, "sense_gain": trained - trained_scr,
        "trained_forward_frac": trained_fwd, "untrained_forward_frac": naive_fwd,
        "collapsed01": float(trained < COLLAPSED),
        "train_food_first_quarter": float(np.mean(curve[:q])),
        "train_food_last_quarter": float(np.mean(curve[-q:])),
    }


def _job(args):
    return run_single(*args)


def run_single_conditions(conditions: dict, seeds: int, seed_start: int, train_episodes: int,
                          test_worlds: int, test_seed_start: int) -> dict:
    """``conditions`` maps a name to world-config overrides. Training seeds and
    test worlds are shared across conditions, so differences are paired."""
    jobs, keys = [], []
    for name, over in conditions.items():
        for s in range(seed_start, seed_start + seeds):
            jobs.append(({**over, "seed": s}, train_episodes, test_worlds, test_seed_start))
            keys.append(name)
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        out = list(ex.map(_job, jobs))
    return {"raw": {n: [r for k, r in zip(keys, out) if k == n] for n in conditions}}
