"""A 2-D artificial-life world driven by a spiking neural network.

This module implements the full, testable causal chain required by the
NeuralMind Artificial Life Playground:

    world state -> egocentric sensory observations -> input currents
    -> LIF spiking dynamics -> action-population competition (soft WTA)
    -> executed action -> world consequences -> shaped reward
    -> reward-prediction-error -> reward-modulated STDP (eligibility)
    -> changed synaptic weights -> subsequent decisions.

The environment uses simple physics for movement, collisions and energy
accounting ONLY. It never selects the agent's high-level action — that is
decided solely by which action population fires most. When plasticity is
disabled the same network still drives behaviour, so the learning condition can
be compared against a genuine no-learning control.

Deliberate approximations (documented honestly, not biological claims):
* Discrete 3-way action set (turn-left / forward / turn-right).
* Reward is *shaped* with an approach term for learnability; this is an
  engineering choice, stated explicitly, not a biological reward signal.
* Sensors are a small egocentric set (food/threat in 3 angular bins + hunger).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np

from neuralmind.affect.reward import RewardPredictor
from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFPopulation
from neuralmind.core.plasticity import STDPConfig

ACTIONS = ("left", "forward", "right")


@dataclass
class WorldConfig:
    size: float = 1.0
    n_food: int = 8
    n_hazard: int = 2
    eat_radius: float = 0.05
    hazard_radius: float = 0.09
    sensor_range: float = 0.6
    speed: float = 0.022          # forward distance per tick
    turn: float = 0.5             # radians turned by left/right actions
    e0: float = 1.0               # initial energy
    food_energy: float = 0.35     # energy gained per food
    move_cost: float = 0.004      # energy per tick (metabolism + movement)
    hazard_cost: float = 0.04     # energy lost per tick inside a hazard
    max_ticks: int = 500
    # neural / learning
    n_action: int = 8
    substeps: int = 8             # SNN steps integrated per world tick
    idle_drive: float = 3.0       # baseline input current (nA)
    sensor_gain: float = 8.0      # sensor signal -> input current
    action_noise: float = 3.5     # exploration noise into action pops (prevents lock-in)
    w_init: float = 1.2
    w_max: float = 4.0
    w_inhib: float = 0.8
    lr: float = 0.8               # reward -> weight-change scale
    normalize: bool = False       # optional homeostatic input normalization
    reward_mode: str = "align"    # "align" (reward turning toward food) or "approach"
    r_eat: float = 1.0
    r_approach: float = 5.0       # approach-shaping weight (approach mode)
    r_align: float = 4.0          # alignment-shaping weight (align mode)
    r_hazard: float = 1.0
    seed: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


class World2D:
    """A single neural agent foraging in a 2-D world."""

    N_SENSORS = 7  # 3 food bins + 3 threat bins + 1 hunger

    def __init__(self, config: WorldConfig | None = None) -> None:
        self.cfg = config or WorldConfig()
        self.reset(self.cfg.seed)

    # ---- setup ----------------------------------------------------------
    def reset(self, seed: int | None = None, keep_weights: bool = False) -> None:
        """Reset the episode. With ``keep_weights`` the learned synaptic weights
        are preserved (membrane state is still cleared) so an agent can be
        trained across multiple episodes."""
        c = self.cfg
        if seed is not None:
            self.seed = int(seed)
            self.rng = np.random.default_rng(self.seed)
        elif not hasattr(self, "rng"):
            self.rng = np.random.default_rng(self.seed)
        self.t = 0
        self.alive = True
        self.energy = c.e0
        self.food_eaten = 0
        self.hazard_hits = 0
        self.distance = 0.0
        self.total_reward = 0.0

        self.agent = np.array([c.size / 2, c.size / 2], dtype=float)
        self.heading = float(self.rng.uniform(0, 2 * math.pi))
        self.food = self._scatter(c.n_food)
        self.hazards = self._scatter(c.n_hazard, margin=0.15)

        if keep_weights and hasattr(self, "net"):
            self.net.reset()  # clears membrane/traces/eligibility, keeps weights
            self._glow[:] = 0.0
        else:
            self._build_network()
        self.predictor = RewardPredictor(alpha=0.2)
        self._prev_food_dist = self._nearest_food_dist()
        self._prev_align = self._food_alignment()
        self.last_action = 1
        self.last_scores = np.zeros(3)

    def _scatter(self, n: int, margin: float = 0.05) -> np.ndarray:
        c = self.cfg
        return self.rng.uniform(margin, c.size - margin, size=(n, 2))

    def _build_network(self) -> None:
        c = self.cfg
        net = SpikingNetwork(dt=1.0)
        net.add_population("sensory", LIFPopulation(self.N_SENSORS, dt=1.0))
        # Reward-modulated *Hebbian* rule: with sustained sensor+action
        # co-activation within a tick, pair-based STDP with a_minus > a_plus
        # yields net depression of the co-active (correct) pathway, which — via
        # normalization — inverts the learned mapping. Using potentiation only
        # (a_minus = 0) makes the eligibility a positive co-activation trace, so
        # a positive reward strengthens the sensors that drove the chosen action.
        stdp = STDPConfig(a_plus=0.02, a_minus=0.0, w_max=c.w_max, tau_eligibility=100.0)
        w0 = np.clip(self.rng.normal(c.w_init, c.w_init * 0.2,
                                     size=(c.n_action, self.N_SENSORS)), 0.0, c.w_max)
        for a in ACTIONS:
            net.add_population(a, LIFPopulation(c.n_action, dt=1.0))
            net.connect(Connection("sensory", a, weights=w0.copy(), tau_syn=5.0,
                                   plastic=True, stdp_config=stdp))
        inhib = -abs(c.w_inhib) * np.ones((c.n_action, c.n_action))
        for i, a in enumerate(ACTIONS):
            for b in ACTIONS:
                if a != b:
                    net.connect(Connection(a, b, weights=inhib.copy(), tau_syn=10.0))
        net.build()
        self.net = net
        self._plastic = [cn for cn in net.connections if cn.plastic]
        self._row_budget = c.w_init * self.N_SENSORS
        # Node bookkeeping for the brain scanner (sensory, then the 3 actions).
        self._node_order = list(net.populations)
        self._node_offsets, off = {}, 0
        for p in self._node_order:
            self._node_offsets[p] = off
            off += net.populations[p].n
        self._n_nodes = off
        self._glow = np.zeros(off)

    def _normalize(self) -> None:
        """Homeostatic input normalization: keep each action neuron's total
        incoming sensory weight constant, so learning redistributes *which*
        sensors drive an action rather than letting one action saturate."""
        for cn in self._plastic:
            rs = cn.weights.sum(axis=1, keepdims=True)
            rs[rs < 1e-9] = 1e-9
            cn.weights *= self._row_budget / rs

    # ---- sensing --------------------------------------------------------
    def _nearest_food_dist(self) -> float:
        if len(self.food) == 0:
            return self.cfg.sensor_range
        d = np.linalg.norm(self.food - self.agent, axis=1)
        return float(d.min())

    def _food_alignment(self) -> float:
        """cos of the angle between heading and the bearing to nearest food
        (1 = facing it directly, -1 = facing away)."""
        if len(self.food) == 0:
            return 0.0
        d = np.linalg.norm(self.food - self.agent, axis=1)
        p = self.food[int(np.argmin(d))]
        bearing = math.atan2(p[1] - self.agent[1], p[0] - self.agent[0])
        return math.cos(bearing - self.heading)

    def _bin_signals(self, points: np.ndarray) -> np.ndarray:
        """Egocentric signal in 3 bins (left/front/right) for a set of points."""
        c = self.cfg
        sig = np.zeros(3)
        if len(points) == 0:
            return sig
        bin_dirs = np.array([self.heading + 0.9, self.heading, self.heading - 0.9])
        for p in points:
            dv = p - self.agent
            dist = math.hypot(dv[0], dv[1])
            if dist > c.sensor_range or dist < 1e-9:
                continue
            bearing = math.atan2(dv[1], dv[0])
            prox = 1.0 - dist / c.sensor_range
            for k in range(3):
                align = math.cos(bearing - bin_dirs[k])
                if align > 0:
                    sig[k] += (align ** 2) * prox
        return np.clip(sig, 0.0, 1.0)

    def sense(self) -> np.ndarray:
        """Return the 7-vector of egocentric sensory signals in [0, 1]."""
        food = self._bin_signals(self.food)
        threat = self._bin_signals(self.hazards)
        hunger = float(np.clip(1.0 - self.energy / self.cfg.e0, 0.0, 1.0))
        return np.concatenate([food, threat, [hunger]])

    # ---- acting ---------------------------------------------------------
    def _decide(self, sensors: np.ndarray) -> tuple[int, np.ndarray, dict]:
        """Run the SNN for substeps under the sensory drive; pick an action."""
        c = self.cfg
        current = c.idle_drive + c.sensor_gain * sensors
        counts = np.zeros(3)
        spikes_any = {p: np.zeros(self.net.populations[p].n, bool)
                      for p in self._node_order}
        for _ in range(c.substeps):
            ext = {"sensory": current}
            for a in ACTIONS:
                ext[a] = self.rng.normal(0.0, c.action_noise, size=c.n_action)
            s = self.net.step(external=ext)
            for p in self._node_order:
                spikes_any[p] |= s[p]
            for i, a in enumerate(ACTIONS):
                counts[i] += int(s[a].sum())
        # Update the per-node decaying glow used by the brain scanner.
        self._glow *= 0.55
        for p in self._node_order:
            o = self._node_offsets[p]
            self._glow[o:o + spikes_any[p].size] = np.maximum(
                self._glow[o:o + spikes_any[p].size], spikes_any[p].astype(float))
        if counts.max() == counts.min():
            action = int(self.rng.integers(0, 3))
        else:
            action = int(np.argmax(counts))
        return action, counts, spikes_any

    def _move(self, action: int) -> None:
        c = self.cfg
        if action == 0:       # left
            self.heading += c.turn
            step = c.speed * 0.5
        elif action == 2:     # right
            self.heading -= c.turn
            step = c.speed * 0.5
        else:                 # forward
            step = c.speed
        self.heading %= 2 * math.pi
        nx = self.agent[0] + step * math.cos(self.heading)
        ny = self.agent[1] + step * math.sin(self.heading)
        # Reflect off walls.
        if nx < 0 or nx > c.size:
            self.heading = math.pi - self.heading
            nx = min(max(nx, 0.0), c.size)
        if ny < 0 or ny > c.size:
            self.heading = -self.heading
            ny = min(max(ny, 0.0), c.size)
        self.distance += math.hypot(nx - self.agent[0], ny - self.agent[1])
        self.agent = np.array([nx, ny])

    # ---- one tick -------------------------------------------------------
    def step(self, learning: bool = True) -> dict:
        """Advance the world by one tick and return a frame of state."""
        if not self.alive:
            return self._frame(0, np.zeros(3), 0.0, 0.0)
        c = self.cfg
        sensors = self.sense()
        action, scores, spikes = self._decide(sensors)
        self._move(action)

        # Consequences.
        eaten = 0
        d = np.linalg.norm(self.food - self.agent, axis=1) if len(self.food) else np.array([])
        for idx in np.nonzero(d < c.eat_radius)[0] if d.size else []:
            eaten += 1
            self.food[idx] = self._scatter(1)[0]
        self.food_eaten += eaten
        self.energy += eaten * c.food_energy

        in_hazard = False
        if len(self.hazards):
            dh = np.linalg.norm(self.hazards - self.agent, axis=1)
            in_hazard = bool((dh < c.hazard_radius).any())
        if in_hazard:
            self.hazard_hits += 1
            self.energy -= c.hazard_cost

        self.energy -= c.move_cost
        self.energy = min(self.energy, 1.5 * c.e0)

        # Shaped reward. On an eat tick the shaping term is skipped because food
        # respawned (the geometry jumps); the eat reward stands on its own.
        new_food_dist = self._nearest_food_dist()
        new_align = self._food_alignment()
        if c.reward_mode == "align":
            # Reward turning the heading toward the nearest food. This teaches
            # the sensor->turn mapping directly and does not give "forward" free
            # credit the way a pure distance term does.
            shaped = 0.0 if eaten else c.r_align * (new_align - self._prev_align)
        else:
            shaped = 0.0 if eaten else c.r_approach * (self._prev_food_dist - new_food_dist)
        self._prev_food_dist = new_food_dist
        self._prev_align = new_align
        reward = c.r_eat * eaten + shaped - c.r_hazard * (1.0 if in_hazard else 0.0)
        self.total_reward += reward

        # Learning: RPE modulates eligibility-based STDP.
        rpe = self.predictor.update(reward)
        if learning:
            self.net.apply_reward(c.lr * rpe)
            if c.normalize:
                self._normalize()
        self.net.clear_eligibility()

        self.t += 1
        if self.energy <= 0 or self.t >= c.max_ticks:
            self.alive = False
        self.last_action, self.last_scores = action, scores
        return self._frame(action, scores, reward, rpe, spikes)

    def _frame(self, action, scores, reward, rpe, spikes=None) -> dict:
        return {
            "t": self.t,
            "agent": [round(float(self.agent[0]), 4), round(float(self.agent[1]), 4)],
            "heading": round(self.heading, 4),
            "energy": round(float(self.energy), 4),
            "food": [[round(float(x), 4), round(float(y), 4)] for x, y in self.food],
            "action": int(action),
            "scores": [int(s) for s in scores],
            "reward": round(float(reward), 4),
            "rpe": round(float(rpe), 4),
            "food_eaten": self.food_eaten,
            "hazard_hits": self.hazard_hits,
            "alive": self.alive,
            "glow": self.neural_glow(),  # per-node spike glow for the brain scanner
        }

    def neural_glow(self) -> list[float]:
        """Per-node decaying spike activity in node order (sensory, then actions)."""
        return [round(float(x), 3) for x in self._glow]

    def brain_layout(self) -> dict:
        """3-D node layout + edges + connectivity matrix for the brain scanner."""
        from neuralmind.recorder import build_layout
        return build_layout(self.net, seed=self.seed)

    def hazard_list(self) -> list[list[float]]:
        return [[round(float(x), 4), round(float(y), 4)] for x, y in self.hazards]

    # ---- episodes -------------------------------------------------------
    def run(self, ticks: int | None = None, learning: bool = True) -> dict:
        """Run until death or ``ticks``/max_ticks; return summary metrics."""
        ticks = ticks or self.cfg.max_ticks
        energy_trace = []
        while self.alive and self.t < ticks:
            self.step(learning=learning)
            energy_trace.append(round(float(self.energy), 4))
        return {
            "food_eaten": self.food_eaten,
            "survival_ticks": self.t,
            "total_reward": round(self.total_reward, 3),
            "hazard_hits": self.hazard_hits,
            "distance": round(self.distance, 3),
            "mean_energy": round(float(np.mean(energy_trace)) if energy_trace else 0.0, 4),
            "final_energy": round(float(self.energy), 4),
        }
