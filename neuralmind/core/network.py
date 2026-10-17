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

Fused stepping
--------------
When every population is a plain :class:`LIFPopulation` with the same
parameters, :meth:`SpikingNetwork.build` stacks all membrane state, all
synaptic currents and, per presynaptic population, all outgoing weight
matrices into shared arrays (the populations and connections hold views into
them). :meth:`SpikingNetwork.step` then advances the network with a handful of
whole-array operations. It performs the same floating-point operations in the
same order as the per-object path, so results are bit-identical;
``tests/test_network.py`` checks this.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from neuralmind.core._bound import Bound
from neuralmind.core.neurons import LIFPopulation
from neuralmind.core.plasticity import STDPConfig, STDPSynapse


@dataclass
class Connection(Bound):
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
        self._fused: _Fused | None = None

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
        self._fused = _Fused.try_build(self)
        self._built = True

    def reset(self) -> None:
        if not self._built:
            self.build()
        for pop in self.populations.values():
            pop.reset()
        for c in self.connections:
            c.reset()
        if self._fused is not None:
            self._fused.reset()
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
        if self._fused is not None and not self._fused.dirty:
            spikes = self._fused.step(external, modulator)
            self.t += self.dt
            return spikes
        if self._fused is not None:          # an array was rebound from outside
            self._fused.hand_back()
            self._fused = None

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


class _Fused:
    """Stacked state and whole-array stepping for a homogeneous LIF network."""

    @classmethod
    def try_build(cls, net: SpikingNetwork) -> _Fused | None:
        pops = list(net.populations.values())
        if not pops or any(type(p) is not LIFPopulation for p in pops):
            return None
        if any(p.params != pops[0].params or p.dt != net.dt for p in pops):
            return None
        return cls(net)

    def __init__(self, net: SpikingNetwork) -> None:
        self.net = net
        self.dirty = False
        self.names = list(net.populations)
        pops = [net.populations[n] for n in self.names]
        self.pops = pops
        self.params, self.dt = pops[0].params, net.dt
        self.sl, off = {}, 0
        for n, p in zip(self.names, pops):
            self.sl[n] = slice(off, off + p.n)
            off += p.n
        self.n = off
        self.v = np.concatenate([p.v for p in pops])
        self.ref = np.concatenate([p.refractory_left for p in pops])
        conns = net.connections
        self.conns = conns
        # Synaptic currents and weights, grouped by presynaptic population.
        # The current vector ends with one permanent zero, used as padding.
        self.groups, rows, r = [], {}, 0
        n_syn = sum(net.populations[c.post].n for c in conns)
        self.i_syn = np.zeros(n_syn + 1)
        self.decay = np.ones(n_syn + 1)
        bound = []
        for pre in self.names:
            out = [c for c in conns if c.pre == pre]
            if not out:
                continue
            start = r
            w = np.vstack([c.weights for c in out])
            o = 0
            for c in out:
                k = c.weights.shape[0]
                self.i_syn[r:r + k] = c._i_syn
                bound += [(c, "weights", w[o:o + k]), (c, "_i_syn", self.i_syn[r:r + k])]
                self.decay[r:r + k] = c._decay
                rows[id(c)] = (r, k)
                o += k
                r += k
            self.groups.append((self.sl[pre], slice(start, r), w))
        # gather[k, j]: index into i_syn (or the zero pad) of the k-th
        # connection into neuron j, in connection order.
        into = {n: [c for c in conns if c.post == n] for n in self.names}
        depth = max([len(v) for v in into.values()] + [0])
        self.gather = np.full((depth, self.n), n_syn, dtype=np.intp)
        for n, cs in into.items():
            for k, c in enumerate(cs):
                r0, m = rows[id(c)]
                self.gather[k, self.sl[n]] = np.arange(r0, r0 + m)
        # Eligibility-mode, potentiation-only STDP on connections that share
        # a presynaptic population and a config is stepped as one block.
        self.stdp_blocks, self.stdp_single = [], []
        plastic = [c for c in conns if c._stdp is not None]
        keys = {}
        for c in plastic:
            cfg = c._stdp.config
            if cfg.tau_eligibility is None or cfg.a_minus != 0.0:
                self.stdp_single.append(c)
            else:
                keys.setdefault((c.pre, cfg), []).append(c)
        for (pre, cfg), cs in keys.items():
            syns = [c._stdp for c in cs]
            xp = np.vstack([q.x_pre for q in syns])
            xq = np.concatenate([q.x_post for q in syns])
            el = np.vstack([q.eligibility for q in syns])
            owner = np.repeat(np.arange(len(cs)), [q.x_post.size for q in syns])
            post_idx = np.concatenate([np.arange(self.sl[c.post].start, self.sl[c.post].stop) for c in cs])
            o = 0
            for j, (c, q) in enumerate(zip(cs, syns)):
                m = q.x_post.size
                bound += [(q, "x_pre", xp[j]), (q, "x_post", xq[o:o + m]), (q, "eligibility", el[o:o + m])]
                o += m
            d = (np.exp(-self.dt / cfg.tau_plus), np.exp(-self.dt / cfg.tau_minus),
                 np.exp(-self.dt / cfg.tau_eligibility))
            self.stdp_blocks.append((cs, self.sl[pre], post_idx, owner, xp, xq, el, cfg, d))
        for n, p in zip(self.names, pops):
            bound += [(p, "v", self.v[self.sl[n]]), (p, "refractory_left", self.ref[self.sl[n]])]
        for obj, name, view in bound:
            object.__setattr__(obj, name, view)
            object.__setattr__(obj, "_fused_owner", self)
        self.bound_objs = [obj for obj, _, _ in bound]
        self.prev = np.zeros(self.n)

    def reset(self) -> None:
        self.prev[:] = 0.0

    def hand_back(self) -> None:
        """Leave the per-object path the state it needs to continue exactly."""
        for c in self.conns:
            x = self.prev[self.sl[c.pre]]
            c._pre_spikes_prev = x > 0
            c._pre_any = bool(x.any())
            c._pre_f = x.copy()
        for obj in {id(o): o for o in self.bound_objs}.values():
            object.__setattr__(obj, "_fused_owner", None)

    def step(self, external: dict, modulator: float) -> dict[str, np.ndarray]:
        p, dt = self.params, self.dt
        # 1. Decay all synaptic currents and add last step's spikes.
        i_syn = self.i_syn
        i_syn *= self.decay
        prev = self.prev
        for pre_sl, rows, w in self.groups:
            x = prev[pre_sl]
            if x.any():
                i_syn[rows] += w @ x
        total = np.zeros(self.n)
        for row in i_syn[self.gather]:
            total += row
        if external:
            ext = np.zeros(self.n)
            for name, e in external.items():
                if name not in self.sl:
                    raise ValueError(f"external input for unknown population '{name}'")
                ext[self.sl[name]] = np.asarray(e, dtype=np.float64)
            total += ext
        # 2. Integrate every population at once (same arithmetic as LIFPopulation.step).
        v, ref = self.v, self.ref
        active = ref <= 0.0
        dv = (dt / p.tau_m) * (-(v - p.v_rest) + p.r_m * total)
        v[:] = np.where(active, v + dv, p.v_reset)
        spiked = active & (v >= p.v_threshold)
        v[:] = np.where(spiked, p.v_reset, v)
        ref[:] = np.where(spiked, p.refractory, np.maximum(0.0, ref - dt))
        spikes = {}
        for n, pop in zip(self.names, self.pops):
            s = spiked[self.sl[n]]
            spikes[n] = s
            pop.spikes = s
            pop.t += dt
        # 3. Plasticity, then remember the spikes for next step's transmission.
        for cs, pre_sl, post_idx, owner, xp, xq, el, cfg, (d_plus, d_minus, d_elig) in self.stdp_blocks:
            if not all(c.plastic for c in cs):
                for c in cs:
                    if c.plastic:
                        c._stdp.update(c.weights, spikes[c.pre], spikes[c.post], dt, modulator)
                continue
            post = spiked[post_idx]
            xp *= d_plus
            xq *= d_minus
            xp[:, spiked[pre_sl]] += 1.0
            xq[post] += 1.0
            el *= d_elig
            if post.any():
                el += cfg.a_plus * (post.astype(np.float64)[:, None] * xp[owner])
        for c in self.stdp_single:
            if c.plastic:
                c._stdp.update(c.weights, spikes[c.pre], spikes[c.post], dt, modulator)
        self.prev = spiked.astype(np.float64)
        return spikes
