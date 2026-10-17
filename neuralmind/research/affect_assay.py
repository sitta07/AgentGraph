"""Behavioural assay for emotion-like internal states (evolve_affect).

Follows the "emotion primitives" framing of Anderson & Adolphs (2014) and the
fly assay of Gibson et al. (2015): an internal state is emotion-like if a
brief stimulus changes behaviour for longer than the stimulus lasts
(persistence), more for a stronger stimulus (scalability), and in opposite
directions for good and bad stimuli (valence).

Each tested agent is copied, frozen, into an empty arena (no food, no
hazards, alone). A pulse is injected into its affect state at tick 0 as if it
had received that input once; the same world seed is run with and without
the pulse with fresh noise every tick and energy held at its start value,
so with no affect output both runs are identical. Behaviour is the
histogram of chosen actions per window of ticks, pooled over repeats.
"""

from __future__ import annotations

import numpy as np

from neuralmind.world import AFFECT_INPUTS, World2D, WorldConfig

PULSES = {"pain1": ("pain", 1.0), "pain3": ("pain", 3.0), "food1": ("food", 1.0)}


def _actions(cfg: dict, agent, pulse: tuple | None, seed: int, ticks: int) -> list[int]:
    w = World2D(WorldConfig(**{**cfg, "seed": seed}))
    ag = w.agents[0]
    ag.build_net(np.random.default_rng(0), genome={"w": agent.genome["w"]})
    ag.aggr_gain = agent.aggr_gain
    ag.aff_A, ag.aff_B, ag.aff_logit = agent.aff_A.copy(), agent.aff_B.copy(), agent.aff_logit.copy()
    ag.aff_s = np.zeros(cfg["affect_k"])
    if pulse is not None:
        x = np.zeros(len(AFFECT_INPUTS))
        x[AFFECT_INPUTS.index(pulse[0])] = pulse[1]
        ag.aff_s = ag.aff_A @ x
    out = []
    for t in range(ticks):
        # Fresh noise per tick and clamped energy: with or without a pulse the
        # agent sees the same inputs and noise, so only its affect state differs.
        w.rng = np.random.default_rng((seed, t))
        ag.energy = w.cfg.e0
        w.step(learning=False)
        out.append(ag.last_action)
    return out


def _hist(runs: list[list[int]], lo: int, hi: int, k: int) -> np.ndarray:
    h = np.bincount([a for r in runs for a in r[lo:hi]], minlength=k).astype(float)
    return h / h.sum()


def assay(world_cfg, agents: list, repeats: int = 8, ticks: int = 20, unmask: bool = True) -> dict:
    """Mean emotion-primitive scores over ``agents``. ``unmask`` lets the
    affect state act even in a numb_affect population, so drifted genes can
    be compared with selected ones."""
    cfg = {**world_cfg.as_dict(), "n_agents": 1, "n_food": 0, "n_hazard": 0, "evolve": False,
           "numb_affect": world_cfg.numb_affect and not unmask}
    cfg.pop("seed", None)
    k = 6 if cfg.get("social") else 3
    rows = []
    for agent in agents:
        runs = {name: [_actions(cfg, agent, p, 500 + r, ticks) for r in range(repeats)]
                for name, p in (("base", None), *PULSES.items())}
        tv = lambda a, lo, hi: 0.5 * float(np.abs(_hist(runs[a], lo, hi, k) - _hist(runs["base"], lo, hi, k)).sum())
        d_pain = _hist(runs["pain1"], 0, 10, k) - _hist(runs["base"], 0, 10, k)
        d_food = _hist(runs["food1"], 0, 10, k) - _hist(runs["base"], 0, 10, k)
        n = np.linalg.norm(d_pain) * np.linalg.norm(d_food)
        rows.append({"affect_early": tv("pain1", 0, 5),
                     "affect_persistence": tv("pain1", 5, ticks),
                     "affect_scalability": tv("pain3", 0, 10) - tv("pain1", 0, 10),
                     "affect_valence_cos": float(d_pain @ d_food / n) if n > 0 else float("nan")})
    if not rows:
        return {}
    mean = lambda v: float(np.mean(v)) if v else float("nan")
    return {key: mean([r[key] for r in rows if not np.isnan(r[key])]) for key in rows[0]}


def gene_summary(agents: list) -> dict:
    if not agents:
        return {}
    decay = np.array([1.0 / (1.0 + np.exp(-a.aff_logit)) for a in agents])
    return {"affect_decay": float(decay.mean()),
            "affect_out_norm": float(np.mean([np.abs(a.aff_B).sum() for a in agents])),
            "affect_pain_in": float(np.mean([np.abs(a.aff_A[:, 0]).sum() for a in agents]))}
