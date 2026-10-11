"""PettingZoo ``ParallelEnv`` wrapper around :class:`~neuralmind.world.World2D`.

Lets any multi-agent RL algorithm control agents in the same world where other
agents are driven by spiking-network brains, so learned policies and SNN brains
can be compared, or mixed, under identical physics, food, hazards and social
rules.

    from neuralmind.envs import parallel_env
    env = parallel_env(n_rl=4, n_snn=4, config={"social": True})
    obs, infos = env.reset(seed=0)
    while env.agents:
        actions = {a: env.action_space(a).sample() for a in env.agents}
        obs, rewards, terms, truncs, infos = env.step(actions)

* Observations: the agent's egocentric sensor vector in [0, 1]. The layout is
  food x3, threat x3, hunger, plus (if social) other-agents x3 and heard
  signal.
* Actions: ``Discrete(k)`` over left / forward / right, plus (if social)
  attack / share / signal.
* Rewards: the same per-tick reward the SNN agents learn from.
* Termination is death (energy <= 0). Truncation is ``max_cycles``.
* SNN agents (``n_snn``) are part of the environment and are not exposed as
  RL agents.

Requires the optional dependencies ``pettingzoo`` and ``gymnasium`` (MIT).
"""

from __future__ import annotations

import numpy as np
from gymnasium import spaces
from pettingzoo import ParallelEnv

from neuralmind.world import World2D, WorldConfig


class NeuralMindParallelEnv(ParallelEnv):
    metadata = {"name": "neuralmind_v0", "render_modes": ["ansi"], "is_parallelizable": True}

    def __init__(self, n_rl: int = 2, n_snn: int = 0, config: dict | None = None,
                 max_cycles: int = 500, snn_learning: bool = True,
                 render_mode: str | None = None) -> None:
        if n_rl < 1:
            raise ValueError("n_rl must be >= 1")
        cfg = dict(config or {})
        if cfg.get("evolve"):
            raise ValueError("evolve=True is not supported: PettingZoo needs a fixed agent set")
        self.base_cfg = cfg
        self.n_rl, self.n_snn = int(n_rl), int(n_snn)
        self.max_cycles = int(max_cycles)
        self.snn_learning = snn_learning
        self.render_mode = render_mode
        self.possible_agents = [f"agent_{i}" for i in range(self.n_rl)]
        self._name_to_id = {name: i for i, name in enumerate(self.possible_agents)}
        probe = World2D(self._cfg(seed=0))
        n_obs = probe.agents[0].n_sensors
        n_act = len(probe.agents[0].actions)
        self.action_names = list(probe.agents[0].actions)
        self._obs_space = spaces.Box(0.0, 1.0, shape=(n_obs,), dtype=np.float32)
        self._act_space = spaces.Discrete(n_act)
        self.world: World2D | None = None
        self.agents: list[str] = []

    def _cfg(self, seed: int) -> WorldConfig:
        return WorldConfig(**{**self.base_cfg, "seed": int(seed),
                              "n_agents": self.n_rl + self.n_snn,
                              "max_ticks": self.max_cycles + 10})

    def observation_space(self, agent: str) -> spaces.Box:
        return self._obs_space

    def action_space(self, agent: str) -> spaces.Discrete:
        return self._act_space

    def _obs(self, name: str) -> np.ndarray:
        ag = self.world.agents[self._name_to_id[name]]
        return np.clip(self.world.observe(ag), 0.0, 1.0).astype(np.float32)

    def reset(self, seed: int | None = None, options: dict | None = None):
        seed = int(seed) if seed is not None else int(self.base_cfg.get("seed", 0))
        self.world = World2D(self._cfg(seed))
        for space in (self._obs_space, self._act_space):
            space.seed(seed)
        self.agents = list(self.possible_agents)
        self._cycles = 0
        return {a: self._obs(a) for a in self.agents}, {a: {} for a in self.agents}

    def step(self, actions: dict):
        if not self.agents:
            return {}, {}, {}, {}, {}
        ids = {self._name_to_id[a]: int(actions[a]) for a in self.agents if a in actions}
        frame = self.world.step(learning=self.snn_learning, actions=ids)
        self._cycles += 1
        byid = {a["id"]: a for a in frame["agents"]}
        obs, rew, term, trunc, info = {}, {}, {}, {}, {}
        for name in self.agents:
            aid = self._name_to_id[name]
            a = byid[aid]
            obs[name] = self._obs(name)
            rew[name] = float(a["reward"])
            term[name] = not a["alive"]
            trunc[name] = self._cycles >= self.max_cycles
            info[name] = {"energy": a["energy"], "food_eaten": a["food_eaten"],
                          "action_name": a["action_name"]}
        self.agents = [n for n in self.agents if not (term[n] or trunc[n])]
        return obs, rew, term, trunc, info

    def render(self):
        if self.render_mode != "ansi" or self.world is None:
            return None
        rows = [f"t={self.world.t} food={len(self.world.food)}"]
        for ag in self.world.agents:
            kind = "RL " if ag.id < self.n_rl else "SNN"
            rows.append(f"{kind} {ag.id}: pos=({ag.pos[0]:.2f},{ag.pos[1]:.2f}) "
                        f"E={ag.energy:.2f} {'alive' if ag.alive else 'dead'}")
        return "\n".join(rows)

    def close(self):
        self.world = None


def parallel_env(**kwargs) -> NeuralMindParallelEnv:
    return NeuralMindParallelEnv(**kwargs)
