"""Tabular Q-learning controllers that live inside an evolving SNN population.

Founders with id < ``founders`` and all their descendants (same lineage) are
driven by a Q-learner instead of their spiking network. Everything else is
identical: body, energy, sensors, actions, reward and reproduction rules.
Whether Q-learner lineages grow or shrink relative to SNN lineages is an
invasion test under identical rules.

* State: the sensor vector binarised to 11 bits (food x3 > 0.2, threat x3 > 0.2,
  hunger > 0.5, others x3 > 0.2, heard signal > 0), i.e. 2048 states.
* Action: epsilon-greedy over the agent's actions, random tie-break.
* Update: one-step Q-learning on the agent's own per-tick reward.
* Inheritance: ``inherit=False`` gives every newborn a zero table;
  ``inherit=True`` gives it a copy of its parent's table at birth.

The policy sees the world at the start of each tick, before other agents move
in that tick; SNN agents sense just before they act. This is a small
information lag for the Q-learners.
"""

from __future__ import annotations

import numpy as np

N_BITS = 11


def state_index(sensors: np.ndarray) -> int:
    s = np.asarray(sensors, dtype=float)
    bits = np.concatenate([s[0:6] > 0.2, [s[6] > 0.5], s[7:10] > 0.2, [s[10] > 0.0]])
    return int(np.dot(bits.astype(int), 1 << np.arange(N_BITS)))


class QPopulation:
    def __init__(self, founders: int, n_actions: int, seed: int, inherit: bool = False,
                 alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.05) -> None:
        self.founders, self.n_actions, self.inherit = int(founders), int(n_actions), bool(inherit)
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.rng = np.random.default_rng(10_007 * (seed + 1))
        self.q: dict[int, np.ndarray] = {}
        self.last: dict[int, tuple[int, int]] = {}

    def controls(self, ag) -> bool:
        return ag.lineage < self.founders

    def _table(self, ag) -> np.ndarray:
        if ag.id not in self.q:
            parent = self.q.get(ag.parent) if self.inherit and ag.parent is not None else None
            self.q[ag.id] = (parent.copy() if parent is not None
                             else np.zeros((1 << N_BITS, self.n_actions)))
        return self.q[ag.id]

    def act(self, world) -> dict[int, int]:
        """Choose actions for every living agent this population controls."""
        out = {}
        for ag in world.agents:
            if not (ag.alive and self.controls(ag)):
                continue
            q = self._table(ag)
            s = state_index(world.observe(ag))
            if self.rng.random() < self.epsilon:
                a = int(self.rng.integers(self.n_actions))
            else:
                row = q[s]
                a = int(self.rng.choice(np.flatnonzero(row == row.max())))
            out[ag.id] = a
            self.last[ag.id] = (s, a)
        return out

    def learn(self, world, frame: dict) -> None:
        """Update each controlled agent's table from the reward it just got."""
        byid = {a.id: a for a in world.agents}
        for rec in frame["agents"]:
            sa = self.last.pop(rec["id"], None)
            if sa is None:
                continue
            s, a = sa
            q = self.q[rec["id"]]
            ag = byid.get(rec["id"])
            if rec["alive"] and ag is not None:
                target = rec["reward"] + self.gamma * q[state_index(world.observe(ag))].max()
            else:
                target = rec["reward"]
            q[s, a] += self.alpha * (target - q[s, a])
        live = {a.id for a in world.agents if a.alive}
        for i in [i for i in self.q if i not in live and i not in byid]:
            del self.q[i]


def invader_share(world, pop: QPopulation) -> float:
    live = [a for a in world.agents if a.alive]
    return sum(pop.controls(a) for a in live) / len(live) if live else float("nan")
