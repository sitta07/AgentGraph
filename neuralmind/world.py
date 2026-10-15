"""A 2-D artificial-life world driven by spiking neural networks.

Implements the full, testable causal chain for the NeuralMind Artificial Life
Playground, for one or several independent neural agents sharing one arena:

    world state -> egocentric sensory observations -> input currents
    -> LIF spiking dynamics -> action-population competition (soft WTA)
    -> executed action -> world consequences -> shaped reward
    -> reward-prediction-error -> reward-modulated Hebbian (eligibility)
    -> changed synaptic weights -> subsequent decisions.

Each agent owns its own network, reward predictor and affect state. The
environment uses simple physics for movement, collisions and energy accounting
ONLY; it never selects an agent's high-level action — that is decided solely by
which action population fires most.

Deliberate approximations (documented, not biological claims):
* Discrete 3-way action set (turn-left / forward / turn-right).
* Reward is *shaped* (alignment-to-food term) for learnability — an engineering
  choice, stated explicitly.
* Small egocentric sensor set (food/threat in 3 angular bins + hunger).
* Affect variables are bounded model quantities, NOT subjective feelings.

Backwards compatibility: ``World2D`` exposes the first agent's state through
``agent``/``heading``/``energy``/``net``/``sense()``/``_decide()``/``_move()``
etc., so single-agent code and tests are unaffected. The random-number draw
order for the first agent does not depend on how many agents there are.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np

from neuralmind.affect.affect_state import AffectState
from neuralmind.affect.reward import RewardPredictor
from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFPopulation
from neuralmind.core.plasticity import STDPConfig

ACTIONS = ("left", "forward", "right")
SOCIAL_ACTIONS = ("attack", "share", "signal")
N_SENSORS = 7          # 3 food bins + 3 threat bins + hunger
N_SOCIAL_SENSORS = 4   # 3 "other agent" bins + heard-signal level


@dataclass
class WorldConfig:
    size: float = 1.0
    n_agents: int = 1
    n_food: int = 8
    n_hazard: int = 2
    eat_radius: float = 0.05
    hazard_radius: float = 0.09
    sensor_range: float = 0.6
    speed: float = 0.022
    turn: float = 0.5
    e0: float = 1.0
    food_energy: float = 0.35
    move_cost: float = 0.004
    hazard_cost: float = 0.04
    max_ticks: int = 500
    n_action: int = 8
    substeps: int = 8
    idle_drive: float = 3.0
    sensor_gain: float = 8.0
    action_noise: float = 3.5
    w_init: float = 1.2
    w_max: float = 4.0
    w_inhib: float = 0.8
    lr: float = 0.8
    normalize: bool = False
    reward_mode: str = "align"
    r_eat: float = 1.0
    r_approach: float = 5.0
    r_align: float = 4.0
    r_hazard: float = 1.0
    ticks_per_day: int = 60
    # --- social layer (opt-in) ---
    social: bool = False
    attack_radius: float = 0.08    # reach for attack / share
    steal: float = 0.15            # energy taken from a victim per hit
    attack_cost: float = 0.02      # energy the attacker spends per attempt
    share_amount: float = 0.10     # energy given per share
    share_benefit: float = 2.0     # recipient gains share_amount * benefit
    signal_range: float = 0.5
    signal_cost: float = 0.002
    r_prosocial: float = 0.0       # Hamilton-style weight on partners' gain/loss
    r_hurt: float = 1.0            # penalty per food-unit of energy stolen from you
    aggression_gain: float = 1.0   # frustration -> current into 'attack' (nA)
    gift_reward: bool = True       # recipients' learning reward counts energy received as a gift
    w_social_scale: float = 0.85   # initial input-weight scale for social actions
    credit_chosen_only: bool = False  # True: reward changes only the executed action's input weights
    frozen_inputs: tuple = ()      # action names whose input weights never learn
    normalized_inputs: tuple = ()  # action names whose per-neuron input sum is held at its innate value
    mirror_at: int = -1            # tick from which left/right sensing is swapped (-1: never)
    deaf: bool = False             # True: the heard-signal sensor always reads 0
    positive_rpe_only: bool = False  # True: negative reward-prediction errors change no weights
    # True: affect (and the frustration->aggression drive) follows the RPE of
    # the primary reward (eating, hazards, theft, being hurt) only.
    # False: affect follows the full learning reward, including shaping.
    affect_from_primary: bool = True
    # --- evolution (opt-in): reproduction with heritable, mutating genomes ---
    evolve: bool = False
    repro_threshold: float = 1.2   # energy needed to reproduce
    repro_cost: float = 0.5        # energy handed from parent to offspring
    max_pop: int = 40
    max_age: int = 1500            # ticks; death of old age keeps turnover going
    mut_sigma: float = 0.15        # weight mutation s.d. (relative to w_init)
    trait_sigma: float = 0.2       # mutation s.d. of the heritable aggression gain
    birth_radius: float = 0.04     # offspring scatter around the parent
    viscous: bool = True           # True: born near parent; False: born anywhere
    born_near_stranger: bool = False  # with viscous=False: born near a random living non-relative instead
    lamarckian: bool = False       # True: inherit LEARNED weights (control)
    neutral_marker: bool = False   # carry a phenotypically silent gene mutated like the aggression gene
    seed: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


class Agent:
    """One neural agent: its brain, body state, learning and affect."""

    N_SENSORS = N_SENSORS

    def __init__(self, cfg: WorldConfig, aid: int = 0) -> None:
        self.cfg = cfg
        self.id = aid
        self.net: SpikingNetwork | None = None
        self.actions = ACTIONS + (SOCIAL_ACTIONS if cfg.social else ())
        self.n_sensors = N_SENSORS + (N_SOCIAL_SENSORS if cfg.social else 0)
        # heritable trait + genealogy (used by evolution; harmless otherwise)
        self.aggr_gain = float(cfg.aggression_gain)
        self.neutral_gene = float(cfg.aggression_gain)   # drift control; never read by behaviour
        self.generation = 0
        self.parent: int | None = None
        self.ancestors: tuple = ()
        self.lineage = aid
        self.age = 0
        self.born = 0
        self.death_tick: int | None = None
        self.genome: dict | None = None

    # ---- lifecycle ------------------------------------------------------
    def spawn(self, pos: np.ndarray, heading: float) -> None:
        """Place the body and reset per-episode metrics (keeps the brain)."""
        self.pos = np.asarray(pos, dtype=float)
        self.heading = float(heading)
        self.energy = self.cfg.e0
        self.alive = True
        self.food_eaten = 0
        self.hazard_hits = 0
        self.distance = 0.0
        self.total_reward = 0.0
        self.last_action = 1
        self.last_scores = np.zeros(3)
        self.predictor = RewardPredictor(alpha=0.2)
        self.primary_predictor = RewardPredictor(alpha=0.2)
        self.affect = AffectState()
        self._prev_food_dist = self.cfg.sensor_range
        self._prev_align = 0.0
        self.attacks = self.attacked = self.shares_given = self.shares_received = 0
        self.signals = 0
        self.signaling = False
        self.pending_hurt = 0.0     # energy lost to attackers since last tick
        self.pending_gift = 0.0     # energy received from sharers since last tick
        self.mirrored = False       # environment shift: left/right sensor bins swapped

    def build_net(self, rng: np.random.Generator, genome: dict | None = None) -> None:
        c = self.cfg
        net = SpikingNetwork(dt=1.0)
        net.add_population("sensory", LIFPopulation(self.n_sensors, dt=1.0))
        # Reward-modulated Hebbian rule (potentiation-only eligibility): a
        # positive reward strengthens the sensors that drove the chosen action.
        stdp = STDPConfig(a_plus=0.02, a_minus=0.0, w_max=c.w_max, tau_eligibility=100.0)
        if genome is None:
            w0 = np.clip(rng.normal(c.w_init, c.w_init * 0.2,
                                    size=(c.n_action, self.n_sensors)), 0.0, c.w_max)
        for a in self.actions:
            net.add_population(a, LIFPopulation(c.n_action, dt=1.0))
            if genome is not None:
                w = genome["w"][a]
            else:
                # Social actions start with weaker (scaled) input so that the naive
                # default behaviour is locomotion; learning can strengthen them.
                w = w0 * (c.w_social_scale if a in SOCIAL_ACTIONS else 1.0)
            net.connect(Connection("sensory", a, weights=w.copy(), tau_syn=5.0,
                                   plastic=True, stdp_config=stdp))
        inhib = -abs(c.w_inhib) * np.ones((c.n_action, c.n_action))
        for a in self.actions:
            for b in self.actions:
                if a != b:
                    net.connect(Connection(a, b, weights=inhib.copy(), tau_syn=10.0))
        net.build()
        self.net = net
        self._plastic = [cn for cn in net.connections if cn.plastic]
        # The genome is the INNATE (pre-learning) wiring plus heritable traits.
        self.genome = {"w": {cn.post: cn.weights.copy() for cn in self._plastic},
                       "aggression_gain": self.aggr_gain}
        self._row_budget = c.w_init * self.n_sensors
        self._innate_rows = {cn.post: cn.weights.sum(axis=1, keepdims=True)
                             for cn in self._plastic}
        self._node_order = list(net.populations)
        self._node_offsets, off = {}, 0
        for p in self._node_order:
            self._node_offsets[p] = off
            off += net.populations[p].n
        self._n_nodes = off
        self._glow = np.zeros(off)

    def reset_membrane(self) -> None:
        self.net.reset()
        self._glow[:] = 0.0

    # ---- normalization --------------------------------------------------
    def _normalize(self) -> None:
        for cn in self._plastic:
            rs = cn.weights.sum(axis=1, keepdims=True)
            rs[rs < 1e-9] = 1e-9
            cn.weights *= self._row_budget / rs

    # ---- sensing --------------------------------------------------------
    def _bin_signals(self, points: np.ndarray) -> np.ndarray:
        c = self.cfg
        sig = np.zeros(3)
        if len(points) == 0:
            return sig
        bin_dirs = np.array([self.heading + 0.9, self.heading, self.heading - 0.9])
        for p in points:
            dv = p - self.pos
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

    def sense(self, food: np.ndarray, hazards: np.ndarray,
              others: np.ndarray | None = None,
              signals: np.ndarray | None = None) -> np.ndarray:
        food_s = self._bin_signals(food)
        threat_s = self._bin_signals(hazards)
        if self.mirrored:
            food_s, threat_s = food_s[::-1], threat_s[::-1]
        hunger = float(np.clip(1.0 - self.energy / self.cfg.e0, 0.0, 1.0))
        base = [food_s, threat_s, [hunger]]
        if self.cfg.social:
            # other agents in 3 egocentric bins; heard calls (emitted last tick)
            others = np.empty((0, 2)) if others is None else others
            signals = np.empty((0, 2)) if signals is None else signals
            heard = 0.0
            for q in ([] if self.cfg.deaf else signals):
                d = float(np.linalg.norm(q - self.pos))
                if d <= self.cfg.signal_range:
                    heard += 1.0 - d / self.cfg.signal_range
            other_s = self._bin_signals(others)
            base += [other_s[::-1] if self.mirrored else other_s, [min(1.0, heard)]]
        return np.concatenate(base)

    def nearest_food_dist(self, food: np.ndarray) -> float:
        if len(food) == 0:
            return self.cfg.sensor_range
        return float(np.linalg.norm(food - self.pos, axis=1).min())

    def food_alignment(self, food: np.ndarray) -> float:
        if len(food) == 0:
            return 0.0
        d = np.linalg.norm(food - self.pos, axis=1)
        p = food[int(np.argmin(d))]
        bearing = math.atan2(p[1] - self.pos[1], p[0] - self.pos[0])
        return math.cos(bearing - self.heading)

    # ---- acting ---------------------------------------------------------
    def decide(self, sensors: np.ndarray, rng: np.random.Generator) -> tuple[int, np.ndarray, dict]:
        c = self.cfg
        current = c.idle_drive + c.sensor_gain * sensors
        k = len(self.actions)
        counts = np.zeros(k)
        spikes_any = {p: np.zeros(self.net.populations[p].n, bool) for p in self._node_order}
        # Frustration -> aggression coupling (hypothesis, Dollard 1939 /
        # Berkowitz 1989): accumulated negative-RPE "frustration" adds a tonic
        # current to the attack population. It biases, never forces, the choice.
        self.aggression_drive = (self.aggr_gain * self.affect.frustration
                                 if c.social else 0.0)
        for _ in range(c.substeps):
            ext = {"sensory": current}
            for a in self.actions:
                ext[a] = rng.normal(0.0, c.action_noise, size=c.n_action)
            if c.social:
                ext["attack"] = ext["attack"] + self.aggression_drive
            s = self.net.step(external=ext)
            for p in self._node_order:
                spikes_any[p] |= s[p]
            for i, a in enumerate(self.actions):
                counts[i] += int(s[a].sum())
        self._glow *= 0.55
        for p in self._node_order:
            o = self._node_offsets[p]
            self._glow[o:o + spikes_any[p].size] = np.maximum(
                self._glow[o:o + spikes_any[p].size], spikes_any[p].astype(float))
        if counts.max() == counts.min():
            action = int(rng.integers(0, k))
        else:
            action = int(np.argmax(counts))
        return action, counts, spikes_any

    def move(self, action: int) -> None:
        c = self.cfg
        if action >= 3:          # attack / share / signal: stand and act
            return
        if action == 0:
            self.heading += c.turn
            step = c.speed * 0.5
        elif action == 2:
            self.heading -= c.turn
            step = c.speed * 0.5
        else:
            step = c.speed
        self.heading %= 2 * math.pi
        nx = self.pos[0] + step * math.cos(self.heading)
        ny = self.pos[1] + step * math.sin(self.heading)
        if nx < 0 or nx > c.size:
            self.heading = math.pi - self.heading
            nx = min(max(nx, 0.0), c.size)
        if ny < 0 or ny > c.size:
            self.heading = -self.heading
            ny = min(max(ny, 0.0), c.size)
        self.distance += math.hypot(nx - self.pos[0], ny - self.pos[1])
        self.pos = np.array([nx, ny])

    def learn_and_affect(self, reward: float, sensors: np.ndarray,
                         in_hazard: bool, learning: bool, hurt: bool = False,
                         primary: float | None = None, action: int | None = None) -> float:
        c = self.cfg
        rpe = self.predictor.update(reward)
        affect_rpe = (self.primary_predictor.update(primary)
                      if (c.affect_from_primary and primary is not None) else rpe)
        if learning and not (c.positive_rpe_only and rpe < 0):
            chosen = self.actions[action] if (c.credit_chosen_only and action is not None) else None
            for cn in self._plastic:
                if cn.post not in c.frozen_inputs and chosen in (None, cn.post):
                    cn.apply_reward(c.lr * rpe)
                    if cn.post in c.normalized_inputs:
                        rs = cn.weights.sum(axis=1, keepdims=True)
                        cn.weights *= self._innate_rows[cn.post] / np.maximum(rs, 1e-9)
            if c.normalize:
                self._normalize()
        self.net.clear_eligibility()
        self.affect.update(rpe=affect_rpe, threat_cue=float(max(sensors[3:6])),
                           pain=1.0 if (in_hazard or hurt) else 0.0,
                           reward_expectation=float(np.clip(self.predictor.value(), 0, 1)))
        return rpe

    def neural_glow(self) -> list[float]:
        return [round(float(x), 3) for x in self._glow]

    def brain_layout(self) -> dict:
        from neuralmind.recorder import build_layout
        return build_layout(self.net, seed=self.cfg.seed)


class World2D:
    """A 2-D arena with shared food/hazards and one or more neural agents."""

    N_SENSORS = N_SENSORS

    def __init__(self, config: WorldConfig | None = None) -> None:
        self.cfg = config or WorldConfig()
        self.reset(self.cfg.seed)

    # ---- setup ----------------------------------------------------------
    def reset(self, seed: int | None = None, keep_weights: bool = False) -> None:
        c = self.cfg
        if seed is not None:
            self.seed = int(seed)
            self.rng = np.random.default_rng(self.seed)
        elif not hasattr(self, "rng"):
            self.rng = np.random.default_rng(self.seed)
        self.t = 0
        self.deprive = False
        self.events: list[dict] = []
        self._signals_prev = np.empty((0, 2))

        reuse = keep_weights and hasattr(self, "agents")
        if not reuse:
            self.agents = [Agent(c, i) for i in range(max(1, c.n_agents))]

        # Agent 0 draws heading, food, hazards, weights in this fixed order,
        # independent of how many agents follow.
        a0 = self.agents[0]
        a0.spawn(np.array([c.size / 2, c.size / 2]),
                 float(self.rng.uniform(0, 2 * math.pi)))
        self.food = self._scatter(c.n_food)
        self.hazards = self._scatter(c.n_hazard, margin=0.15)
        if reuse:
            a0.reset_membrane()
        else:
            a0.build_net(self.rng)
        a0._prev_food_dist = a0.nearest_food_dist(self.food)
        a0._prev_align = a0.food_alignment(self.food)

        # --- extra agents (only when n_agents > 1) ---
        for ag in self.agents[1:]:
            ang = float(self.rng.uniform(0, 2 * math.pi))
            r = c.size * 0.25
            pos = np.array([c.size / 2 + r * math.cos(ang), c.size / 2 + r * math.sin(ang)])
            pos = np.clip(pos, 0.02, c.size - 0.02)
            ag.spawn(pos, float(self.rng.uniform(0, 2 * math.pi)))
            if reuse:
                ag.reset_membrane()
            else:
                ag.build_net(self.rng)
            ag._prev_food_dist = ag.nearest_food_dist(self.food)
            ag._prev_align = ag.food_alignment(self.food)

        # affect readout alias (agent 0)
        self.affect = a0.affect
        self.next_id = len(self.agents)
        self.births = 0
        # Genealogy of every agent that ever lived (kept after bodies are pruned).
        self.registry: dict[int, dict] = {}
        for ag in self.agents:
            self._register(ag)

    def _scatter(self, n: int, margin: float = 0.05) -> np.ndarray:
        c = self.cfg
        if n <= 0:
            return np.empty((0, 2))
        return self.rng.uniform(margin, c.size - margin, size=(n, 2))

    # ---- single-agent compatibility proxies (agent 0) -------------------
    @property
    def agent0(self) -> Agent:
        return self.agents[0]

    @property
    def agent(self) -> np.ndarray:
        return self.agents[0].pos

    @agent.setter
    def agent(self, v) -> None:
        self.agents[0].pos = np.asarray(v, dtype=float)

    @property
    def heading(self) -> float:
        return self.agents[0].heading

    @heading.setter
    def heading(self, v) -> None:
        self.agents[0].heading = float(v)

    @property
    def energy(self) -> float:
        return self.agents[0].energy

    @energy.setter
    def energy(self, v) -> None:
        self.agents[0].energy = float(v)

    def _proxy0(name):  # noqa: N805
        def getter(self):
            return getattr(self.agents[0], name)
        return property(getter)

    alive = _proxy0("alive")
    food_eaten = _proxy0("food_eaten")
    hazard_hits = _proxy0("hazard_hits")
    distance = _proxy0("distance")
    total_reward = _proxy0("total_reward")
    net = _proxy0("net")
    predictor = _proxy0("predictor")
    last_action = _proxy0("last_action")
    last_scores = _proxy0("last_scores")
    _node_order = _proxy0("_node_order")
    _glow = _proxy0("_glow")

    def sense(self) -> np.ndarray:
        return self.agents[0].sense(self.food, self.hazards)

    def _decide(self, sensors: np.ndarray):
        return self.agents[0].decide(sensors, self.rng)

    def _move(self, action: int) -> None:
        self.agents[0].move(action)

    def neural_glow(self) -> list[float]:
        return self.agents[0].neural_glow()

    def brain_layout(self) -> dict:
        return self.agents[0].brain_layout()

    def hazard_list(self) -> list[list[float]]:
        return [[round(float(x), 4), round(float(y), 4)] for x, y in self.hazards]

    # ---- stepping -------------------------------------------------------
    def observe(self, ag: Agent) -> np.ndarray:
        """The agent's current egocentric sensor vector (what its brain sees)."""
        if not self.cfg.social:
            return ag.sense(self.food, self.hazards)
        others = [o for o in self.agents if o is not ag and o.alive]
        others_pos = np.array([o.pos for o in others]) if others else np.empty((0, 2))
        heard = [q for (i, q) in getattr(self, "_signals_prev", []) if i != ag.id]
        return ag.sense(self.food, self.hazards, others_pos,
                        np.array(heard) if heard else np.empty((0, 2)))

    def _advance_agent(self, ag: Agent, learning: bool, forced: int | None = None) -> dict:
        c = self.cfg
        others = [o for o in self.agents if o is not ag and o.alive] if c.social else []
        if c.social:
            ag.signaling = False
            others_pos = np.array([o.pos for o in others]) if others else np.empty((0, 2))
            heard = [q for (i, q) in self._signals_prev if i != ag.id]
            heard = np.array(heard) if heard else np.empty((0, 2))
            sensors = ag.sense(self.food, self.hazards, others_pos, heard)
        else:
            sensors = ag.sense(self.food, self.hazards)
        ag.last_sensors = sensors
        if forced is None:
            action, scores, _ = ag.decide(sensors, self.rng)
        else:                        # externally controlled (e.g. an RL policy)
            action, scores = int(forced), np.zeros(len(ag.actions))
            if not 0 <= action < len(ag.actions):
                raise ValueError(f"action {action} out of range for agent {ag.id}")
        ag.move(action)

        # eating (shared food)
        eaten = 0
        if len(self.food):
            d = np.linalg.norm(self.food - ag.pos, axis=1)
            hit = list(np.nonzero(d < c.eat_radius)[0])
            if hit:
                eaten = len(hit)
                if self.deprive:
                    self.food = np.delete(self.food, hit, axis=0)
                else:
                    for idx in hit:
                        self.food[idx] = self._scatter(1)[0]
        ag.food_eaten += eaten
        ag.energy += eaten * c.food_energy

        in_hazard = False
        if len(self.hazards):
            dh = np.linalg.norm(self.hazards - ag.pos, axis=1)
            in_hazard = bool((dh < c.hazard_radius).any())
        if in_hazard:
            ag.hazard_hits += 1
            ag.energy -= c.hazard_cost
        ag.energy -= c.move_cost

        social_r, hurt = (self._social_effects(ag, action, others)
                          if c.social else (0.0, False))
        ag.energy = min(ag.energy, 1.5 * c.e0)

        new_dist = ag.nearest_food_dist(self.food)
        new_align = ag.food_alignment(self.food)
        if c.reward_mode == "align":
            shaped = 0.0 if eaten else c.r_align * (new_align - ag._prev_align)
        else:
            shaped = 0.0 if eaten else c.r_approach * (ag._prev_food_dist - new_dist)
        ag._prev_food_dist = new_dist
        ag._prev_align = new_align
        primary = c.r_eat * eaten - c.r_hazard * (1.0 if in_hazard else 0.0) + social_r
        reward = primary + shaped
        ag.total_reward += reward

        rpe = ag.learn_and_affect(reward, sensors, in_hazard,
                                  learning and forced is None, hurt=hurt, primary=primary,
                                  action=action)
        if ag.energy <= 0:
            ag.alive = False
        ag.last_action, ag.last_scores = action, scores
        return {"action": action, "scores": scores, "reward": reward, "rpe": rpe}

    def _social_effects(self, ag: Agent, action: int, others: list) -> tuple[float, bool]:
        """Apply attack / share / signal and incoming social consequences.

        Reward accounting is in "food units" (energy / food_energy):
          attack:  +stolen * (1 - r_prosocial)  - attack_cost
          share:   +given  * (r_prosocial * share_benefit - 1)
          victim:  -r_hurt * stolen (next tick, with a pain signal)
          gift:    +received (next tick)
        With r_prosocial = 0 agents are purely selfish; sharing can only pay
        when r * benefit > 1 (Hamilton's rule, rB > C). Nothing here forces an
        agent to act socially — the action itself was chosen by its network.
        """
        c = self.cfg
        unit = 1.0 / max(1e-9, c.food_energy)
        r, hurt = 0.0, False
        if ag.pending_hurt > 0:
            r -= c.r_hurt * ag.pending_hurt * unit
            hurt, ag.pending_hurt = True, 0.0
        if ag.pending_gift > 0:
            if c.gift_reward:
                r += c.r_eat * ag.pending_gift * unit
            ag.pending_gift = 0.0

        name = ag.actions[action]
        target = None
        if name in ("attack", "share") and others:
            d = [float(np.linalg.norm(o.pos - ag.pos)) for o in others]
            j = int(np.argmin(d))
            if d[j] <= c.attack_radius:
                target = others[j]
        if name == "attack":
            ag.attacks += 1
            ag.energy -= c.attack_cost
            r -= c.r_eat * c.attack_cost * unit
            if target is not None:
                amt = min(c.steal, max(0.0, target.energy))
                target.energy -= amt
                target.pending_hurt += amt
                target.attacked += 1
                ag.energy += amt
                r += c.r_eat * amt * unit * (1.0 - c.r_prosocial)
                self.events.append({"type": "attack", "src": ag.id, "dst": target.id,
                                    "amount": round(amt, 3)})
                if target.energy <= 0:
                    target.alive = False
                    self.events.append({"type": "death", "src": ag.id, "dst": target.id})
            else:
                self.events.append({"type": "attack_miss", "src": ag.id})
        elif name == "share" and target is not None:
            amt = min(c.share_amount, max(0.0, ag.energy))
            gift = amt * c.share_benefit
            ag.energy -= amt
            target.energy += gift
            target.pending_gift += gift
            ag.shares_given += 1
            target.shares_received += 1
            r += c.r_eat * amt * unit * (c.r_prosocial * c.share_benefit - 1.0)
            self.events.append({"type": "share", "src": ag.id, "dst": target.id,
                                "amount": round(gift, 3)})
        elif name == "signal":
            ag.energy -= c.signal_cost
            ag.signals += 1
            ag.signaling = True
            self._signals_now.append((ag.id, ag.pos.copy()))
            self.events.append({"type": "signal", "src": ag.id})
        return r, hurt

    def step(self, learning: bool = True, actions: dict | None = None) -> dict:
        """Advance every living agent by one world tick; return a frame.

        ``actions`` optionally maps agent id -> action index for agents driven
        by an external policy; all other agents are driven by their own SNN."""
        actions = actions or {}
        self.events = []
        self._signals_now = []
        results = {}
        mirrored = 0 <= self.cfg.mirror_at <= self.t
        for ag in self.agents:
            ag.mirrored = mirrored
        for ag in self.agents:
            if ag.alive:
                results[ag.id] = self._advance_agent(ag, learning, actions.get(ag.id))
            else:
                results[ag.id] = {"action": ag.last_action, "scores": ag.last_scores,
                                  "reward": 0.0, "rpe": 0.0}
        self._signals_prev = self._signals_now
        if self.cfg.evolve:
            self._life_cycle()
        self.t += 1
        # Evolving worlds are open-ended; other worlds end the episode at max_ticks.
        if self.t >= self.cfg.max_ticks and not self.cfg.evolve:
            for ag in self.agents:
                ag.alive = False
        return self._frame(results)

    # ---- evolution ------------------------------------------------------
    def _life_cycle(self) -> None:
        """Ageing, reproduction and pruning of long-dead bodies."""
        c = self.cfg
        for ag in list(self.agents):
            if not ag.alive:
                if ag.death_tick is None:
                    ag.death_tick = self.t
                rec = self.registry.get(ag.id)
                if rec is not None and rec["died"] is None:
                    rec["died"] = ag.death_tick
                continue
            ag.age += 1
            if ag.age >= c.max_age:
                ag.alive = False
                ag.death_tick = self.t
                if ag.id in self.registry:
                    self.registry[ag.id]["died"] = self.t
                self.events.append({"type": "old_age", "src": ag.id})
        alive = [ag for ag in self.agents if ag.alive]
        for ag in alive:
            if len([a for a in self.agents if a.alive]) >= c.max_pop:
                break
            if ag.energy >= c.repro_threshold:
                self._birth(ag)
        # keep recently-dead bodies (graves) for 60 ticks, never empty the list
        keep = [ag for ag in self.agents
                if ag.alive or (ag.death_tick is not None and self.t - ag.death_tick < 60)]
        self.agents = keep or self.agents[-1:]

    def _register(self, ag: Agent) -> None:
        self.registry[ag.id] = {"id": ag.id, "parent": ag.parent, "lineage": ag.lineage,
                                "generation": ag.generation, "born": ag.born, "died": None,
                                "aggr_gain": round(ag.aggr_gain, 3)}

    def _birth(self, parent: Agent) -> Agent:
        c, rng = self.cfg, self.rng
        child = Agent(c, self.next_id)
        self.next_id += 1
        strangers = ([a for a in self.agents if a.alive and a is not parent
                      and self.relatedness(parent, a) == 0.0]
                     if (c.born_near_stranger and not c.viscous) else [])
        if c.viscous:
            pos = parent.pos + rng.normal(0.0, c.birth_radius, size=2)
        elif strangers:
            host = strangers[int(rng.integers(len(strangers)))]
            pos = host.pos + rng.normal(0.0, c.birth_radius, size=2)
        else:
            pos = rng.uniform(0.05, c.size - 0.05, size=2)
        child.spawn(np.clip(pos, 0.01, c.size - 0.01), float(rng.uniform(0, 2 * math.pi)))
        base = ({cn.post: cn.weights for cn in parent._plastic} if c.lamarckian
                else parent.genome["w"])
        genome_w = {a: np.clip(w + rng.normal(0.0, c.mut_sigma * c.w_init, size=w.shape),
                               0.0, c.w_max) for a, w in base.items()}
        child.aggr_gain = float(max(0.0, parent.genome["aggression_gain"]
                                    + rng.normal(0.0, c.trait_sigma)))
        if c.neutral_marker:
            child.neutral_gene = float(max(0.0, parent.neutral_gene
                                           + rng.normal(0.0, c.trait_sigma)))
        child.build_net(rng, genome={"w": genome_w})
        child.energy = c.repro_cost
        parent.energy -= c.repro_cost
        child.generation = parent.generation + 1
        child.parent = parent.id
        child.ancestors = (parent.id,) + parent.ancestors[:7]
        child.lineage = parent.lineage
        child.born = self.t
        child._prev_food_dist = child.nearest_food_dist(self.food)
        child._prev_align = child.food_alignment(self.food)
        self.agents.append(child)
        self._register(child)
        self.births += 1
        self.events.append({"type": "birth", "src": parent.id, "dst": child.id})
        return child

    def relatedness(self, a: Agent, b: Agent) -> float:
        """Genealogical relatedness 0.5**(steps to the most recent common
        ancestor via both lines), using up to 8 recorded ancestors; 0 if none."""
        pa, pb = (a.id,) + a.ancestors, (b.id,) + b.ancestors
        best = None
        for i, x in enumerate(pa):
            if x in pb:
                d = i + pb.index(x)
                best = d if best is None else min(best, d)
        return 0.0 if best is None else 0.5 ** best

    def _agent_dict(self, ag: Agent, res: dict) -> dict:
        c = self.cfg
        return {
            "id": ag.id,
            "agent": [round(float(ag.pos[0]), 4), round(float(ag.pos[1]), 4)],
            "heading": round(ag.heading, 4),
            "energy": round(float(ag.energy), 4),
            "action": int(res["action"]),
            "scores": [int(s) for s in res["scores"]],
            "reward": round(float(res["reward"]), 4),
            "rpe": round(float(res["rpe"]), 4),
            "food_eaten": ag.food_eaten,
            "hazard_hits": ag.hazard_hits,
            "alive": ag.alive,
            "hunger": round(float(min(1.0, max(0.0, 1.0 - ag.energy / c.e0))), 3),
            "affect": {k: round(v, 3) for k, v in ag.affect.as_dict().items()},
            "glow": ag.neural_glow(),
            "action_name": ag.actions[int(res["action"])],
            **({"attacks": ag.attacks, "attacked": ag.attacked,
                "shares_given": ag.shares_given, "shares_received": ag.shares_received,
                "signals": ag.signals, "signaling": ag.signaling,
                "aggression_drive": round(float(getattr(ag, "aggression_drive", 0.0)), 3)}
               if c.social else {}),
            **({"generation": ag.generation, "lineage": ag.lineage, "age": ag.age,
                "aggr_gain": round(ag.aggr_gain, 3), "parent": ag.parent}
               if c.evolve else {}),
        }

    def _frame(self, results: dict | None = None) -> dict:
        c = self.cfg
        if results is None:
            results = {ag.id: {"action": ag.last_action, "scores": ag.last_scores,
                               "reward": 0.0, "rpe": 0.0} for ag in self.agents}
        idle = lambda ag: {"action": ag.last_action, "scores": ag.last_scores,
                           "reward": 0.0, "rpe": 0.0}
        res = lambda ag: results.get(ag.id) or idle(ag)   # newborns have no result yet
        a0 = self.agents[0]
        frame = self._agent_dict(a0, res(a0))  # agent-0 fields at top level
        frame.update({
            "t": self.t,
            "food": [[round(float(x), 4), round(float(y), 4)] for x, y in self.food],
            "deprive": self.deprive,
            "day": round(self.t / max(1, c.ticks_per_day), 2),
            "agents": [self._agent_dict(ag, res(ag)) for ag in self.agents],
            "events": list(getattr(self, "events", [])),
            "social": c.social,
            "evolve": c.evolve,
            "population": sum(1 for ag in self.agents if ag.alive),
        })
        return frame

    # ---- interaction ----------------------------------------------------
    def place_food(self, x: float, y: float) -> None:
        s = self.cfg.size
        p = [[min(max(float(x), 0.0), s), min(max(float(y), 0.0), s)]]
        self.food = np.vstack([self.food, p]) if len(self.food) else np.array(p)

    def place_food_ahead(self, dist: float | None = None) -> None:
        a0 = self.agents[0]
        dist = self.cfg.sensor_range * 0.5 if dist is None else dist
        self.place_food(a0.pos[0] + dist * math.cos(a0.heading),
                        a0.pos[1] + dist * math.sin(a0.heading))

    def set_deprive(self, on: bool, clear: bool = True) -> None:
        self.deprive = bool(on)
        if on and clear:
            self.food = np.empty((0, 2))
            for ag in self.agents:
                ag._prev_food_dist = self.cfg.sensor_range
                ag._prev_align = 0.0

    # ---- episodes -------------------------------------------------------
    def run(self, ticks: int | None = None, learning: bool = True) -> dict:
        """Run until agent 0 dies or ``ticks``/max_ticks; summary for agent 0."""
        ticks = ticks or self.cfg.max_ticks
        energy_trace = []
        while self.agents[0].alive and self.t < ticks:
            self.step(learning=learning)
            energy_trace.append(round(float(self.agents[0].energy), 4))
        a0 = self.agents[0]
        return {
            "food_eaten": a0.food_eaten,
            "survival_ticks": self.t,
            "total_reward": round(a0.total_reward, 3),
            "hazard_hits": a0.hazard_hits,
            "distance": round(a0.distance, 3),
            "mean_energy": round(float(np.mean(energy_trace)) if energy_trace else 0.0, 4),
            "final_energy": round(float(a0.energy), 4),
        }
