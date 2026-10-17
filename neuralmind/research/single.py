"""Single-agent learning studies: train one agent, then test it on held-out worlds.

Each run trains a fresh agent for ``train_episodes`` episodes (learning on,
weights kept between episodes), or for a total of ``train_ticks`` ticks in
episodes no longer than the test episode, then freezes it and measures food eaten per
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


def _test(w: World2D, seeds: range, scramble: bool, untrained_cfg: dict | None = None,
          attacks: list | None = None, frustration: list | None = None) -> tuple[float, float]:
    food, fwd = [], []
    for s in seeds:
        if untrained_cfg is None:
            w.cfg.scramble_senses = scramble
            w.reset(seed=s, keep_weights=True)
            env = w
        else:
            env = World2D(WorldConfig(**{**untrained_cfg, "seed": s, "scramble_senses": scramble}))
        ag = env.agents[0]
        moves = hits = 0
        fr = []
        attack = ag.actions.index("attack") if "attack" in ag.actions else -1
        for _ in range(env.cfg.max_ticks):
            if not ag.alive:
                break
            env.step(learning=False)
            moves += ag.last_action == 1
            hits += ag.last_action == attack
            fr.append(ag.affect.frustration)
        food.append(ag.food_eaten)
        fwd.append(moves / max(1, env.t))
        if attacks is not None:
            attacks.append(hits / max(1, env.t))
        if frustration is not None:
            frustration.append(float(np.mean(fr)) if fr else 0.0)
    return float(np.mean(food)), float(np.mean(fwd))


def run_single(cfg_kw: dict, train_episodes: int, test_worlds: int, test_seed_start: int,
               train_ticks: int | None = None) -> dict:
    test_len = cfg_kw.get("max_ticks", WorldConfig.max_ticks)
    ep_len = test_len if train_ticks is None else min(test_len, train_ticks)
    episodes = train_episodes if train_ticks is None else train_ticks // ep_len
    w = World2D(WorldConfig(**{**cfg_kw, "max_ticks": ep_len}))
    curve = []
    for ep in range(episodes):
        w.reset(keep_weights=ep > 0)
        curve.append(w.run(learning=True)["food_eaten"])
    w.cfg.max_ticks = test_len
    seeds = range(test_seed_start, test_seed_start + test_worlds)
    base = {k: v for k, v in cfg_kw.items() if k != "seed"}
    trained_att, naive_att, trained_fr, naive_fr = [], [], [], []
    trained, trained_fwd = _test(w, seeds, False, attacks=trained_att, frustration=trained_fr)
    trained_scr, _ = _test(w, seeds, True)
    naive, naive_fwd = _test(w, seeds, False, base, attacks=naive_att, frustration=naive_fr)
    naive_scr, _ = _test(w, seeds, True, base)
    q = max(1, episodes // 4)
    return {
        "trained_food": trained, "trained_food_scrambled": trained_scr,
        "untrained_food": naive, "untrained_food_scrambled": naive_scr,
        "learning_gain": trained - naive, "sense_gain": trained - trained_scr,
        "trained_forward_frac": trained_fwd, "untrained_forward_frac": naive_fwd,
        "trained_attack_frac": float(np.mean(trained_att)), "untrained_attack_frac": float(np.mean(naive_att)),
        "attack_gain": float(np.mean(trained_att) - np.mean(naive_att)),
        "trained_frustration": float(np.mean(trained_fr)), "untrained_frustration": float(np.mean(naive_fr)),
        "frustration_gain": float(np.mean(trained_fr) - np.mean(naive_fr)),
        "collapsed01": float(trained < COLLAPSED), "train_ticks_run": float(episodes * ep_len),
        "train_food_first_quarter": float(np.mean(curve[:q])),
        "train_food_last_quarter": float(np.mean(curve[-q:])),
    }


def _job(args):
    return run_single(*args)


def run_single_conditions(conditions: dict, seeds: int, seed_start: int, train_episodes: int,
                          test_worlds: int, test_seed_start: int,
                          train_ticks: dict | None = None) -> dict:
    """``conditions`` maps a name to world-config overrides; ``train_ticks``
    optionally maps a name to a total training budget in ticks. Training seeds
    and test worlds are shared across conditions, so differences are paired."""
    train_ticks = train_ticks or {}
    jobs, keys = [], []
    for name, over in conditions.items():
        for s in range(seed_start, seed_start + seeds):
            jobs.append(({**over, "seed": s}, train_episodes, test_worlds, test_seed_start,
                         train_ticks.get(name)))
            keys.append(name)
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        out = list(ex.map(_job, jobs))
    return {"raw": {n: [r for k, r in zip(keys, out) if k == n] for n in conditions}}
