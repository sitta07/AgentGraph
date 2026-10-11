"""Spiking network: named populations wired by current-based synapses.

The network is a directed graph of :class:`~neuralmind.core.neurons.LIFPopulation`
nodes connected by :class:`Connection` edges. Each connection holds a weight
matrix ``W`` of shape ``(n_post, n_pre)`` and an exponentially decaying
synaptic current trace. On every step:

1. each connection decays its current trace and adds ``W @ pre_spikes`` for the
   presynaptic spikes from the *previous* step (one-step transmission delay);
2. each population integrates its total synaptic current plus any external
   stimulus and emits spikes;
3. plastic connections update their weights from the new spikes.

The one-step delay makes the update order-independent and deterministic.

Simplifications
---------------
* Single lumped synaptic time constant per connection (no AMPA/NMDA/GABA split).
* Current-based synapses (no voltage-dependent conductances).
* Uniform one-step axonal/synaptic delay rather than per-synapse delays.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from neuralmind.core.neurons import LIFPopulation
from neuralmind.core.plasticity import STDPConfig, STDPSynapse


@dataclass
class Connection:
    """A weighted projection from a presynaptic to a postsynaptic population."""

    pre: str
    post: str
    weights: np.ndarray        # shape (n_post, n_pre)
    tau_syn: float = 5.0       # synaptic current decay (ms)
    plastic: bool = False
    stdp_config: STDPConfig | None = None
    _i_syn: np.ndarray = field(default=None, repr=False)
    _stdp: STDPSynapse | None = field(default=None, repr=False)
    _pre_spikes_prev: np.ndarray = field(default=None, repr=False)

    def init(self, n_pre: int, n_post: int, dt: float) -> None:
        if self.weights.shape != (n_post, n_pre):
            raise ValueError(
                f"weights for {self.pre}->{self.post} must be "
                f"({n_post}, {n_pre}), got {self.weights.shape}"
            )
        if self.tau_syn <= 0:
            raise ValueError("tau_syn must be > 0")
        self.weights = self.weights.astype(np.float64, copy=True)
        self._i_syn = np.zeros(n_post, dtype=np.float64)
        self._pre_spikes_prev = np.zeros(n_pre, dtype=bool)
        self._pre_any = False                      # any spike in _pre_spikes_prev
        self._pre_f = np.zeros(n_pre, dtype=np.float64)
        self._decay = float(np.exp(-dt / self.tau_syn))
        if self.plastic:
            self._stdp = STDPSynapse(n_pre, n_post, self.stdp_config)

    def reset(self) -> None:
        self._i_syn[:] = 0.0
        self._pre_spikes_prev[:] = False
        self._pre_any = False
        if self._stdp is not None:
            self._stdp.reset()

    def propagate(self) -> np.ndarray:
        """Decay the synaptic current and inject last step's presynaptic spikes."""
        self._i_syn *= self._decay
        if self._pre_any:
            self._i_syn += self.weights @ self._pre_f
        return self._i_syn

    def learn(self, pre_spikes: np.ndarray, post_spikes: np.ndarray,
              dt: float, modulator: float = 1.0) -> None:
        # ``plastic`` can be toggled at runtime to freeze learning (e.g. during
        # a recall/test phase) even though the STDP state object still exists.
        if self.plastic and self._stdp is not None:
            self._stdp.update(self.weights, pre_spikes, post_spikes, dt, modulator)

    def apply_reward(self, modulator: float) -> None:
        """Apply accumulated eligibility as a weight change (eligibility mode)."""
        if self.plastic and self._stdp is not None:
            self._stdp.apply_reward(self.weights, modulator)

    def clear_eligibility(self) -> None:
        if self._stdp is not None:
            self._stdp.clear_eligibility()


class SpikingNetwork:
    """Container that steps populations and their connections in lockstep."""

    def __init__(self, dt: float = 1.0) -> None:
        if dt <= 0:
            raise ValueError("dt must be > 0")
        self.dt = float(dt)
        self.populations: dict[str, LIFPopulation] = {}
        self.connections: list[Connection] = []
        self.t = 0.0
        self._built = False

    def add_population(self, name: str, pop: LIFPopulation) -> LIFPopulation:
        if name in self.populations:
            raise ValueError(f"population '{name}' already exists")
        if pop.dt != self.dt:
            raise ValueError(
                f"population '{name}' dt ({pop.dt}) != network dt ({self.dt})"
            )
        self.populations[name] = pop
        self._built = False
        return pop

    def connect(self, conn: Connection) -> Connection:
        for name in (conn.pre, conn.post):
            if name not in self.populations:
                raise ValueError(f"unknown population '{name}' in connection")
        self.connections.append(conn)
        self._built = False
        return conn

    def build(self) -> None:
        for c in self.connections:
            c.init(self.populations[c.pre].n, self.populations[c.post].n, self.dt)
        self._built = True

    def reset(self) -> None:
        if not self._built:
            self.build()
        for pop in self.populations.values():
            pop.reset()
        for c in self.connections:
            c.reset()
        self.t = 0.0

    def step(
        self,
        external: dict[str, np.ndarray | float] | None = None,
        modulator: float = 1.0,
    ) -> dict[str, np.ndarray]:
        """Advance the whole network by ``dt``.

        Parameters
        ----------
        external:
            Optional mapping of population name -> external input current.
        modulator:
            Global scalar passed to every plastic connection (e.g. reward signal).

        Returns
        -------
        dict
            Mapping of population name -> boolean spike vector for this step.
        """
        if not self._built:
            self.build()
        external = external or {}

        # 1. Accumulate synaptic current per population.
        total_current: dict[str, np.ndarray] = {
            name: np.zeros(pop.n) for name, pop in self.populations.items()
        }
        for c in self.connections:
            total_current[c.post] += c.propagate()
        for name, ext in external.items():
            if name not in self.populations:
                raise ValueError(f"external input for unknown population '{name}'")
            total_current[name] = total_current[name] + np.asarray(ext, dtype=np.float64)

        # 2. Integrate populations.
        spikes = {
            name: pop.step(total_current[name])
            for name, pop in self.populations.items()
        }

        # 3. Plastic weight updates and store spikes for next step's transmission.
        fired = {name: bool(s.any()) for name, s in spikes.items()}
        as_f = {name: s.astype(np.float64) for name, s in spikes.items() if fired[name]}
        for c in self.connections:
            if c._stdp is not None and c.plastic:
                c._stdp.update(c.weights, spikes[c.pre], spikes[c.post], self.dt, modulator)
            c._pre_spikes_prev = spikes[c.pre]
            c._pre_any = fired[c.pre]
            if c._pre_any:
                c._pre_f = as_f[c.pre]

        self.t += self.dt
        return spikes

    def apply_reward(self, modulator: float) -> None:
        """Deliver a global reward signal to every plastic connection.

        Used with eligibility-mode STDP (three-factor learning): synapses that
        were recently co-active have a non-zero eligibility trace and are
        changed in proportion to ``modulator`` (e.g. a reward prediction error).
        """
        for c in self.connections:
            c.apply_reward(modulator)

    def clear_eligibility(self) -> None:
        """Zero eligibility traces on all plastic connections (keeps weights)."""
        for c in self.connections:
            c.clear_eligibility()
