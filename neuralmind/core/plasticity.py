"""Spike-timing-dependent plasticity (STDP) and reward modulation.

Scientific basis
----------------
Pair-based STDP: a synapse is potentiated when the presynaptic spike precedes
the postsynaptic spike (pre-before-post) and depressed in the opposite order,
with exponentially decaying time windows. This captures the canonical
experimental finding of Bi & Poo (1998) and the trace-based formulation of
Song, Miller & Abbott (2000) and Morrison, Diesmann & Gerstner (2008).

Reward-modulated STDP (R-STDP): the STDP-induced change is gated by a global
scalar (e.g. a dopamine-like reward-prediction-error signal). This follows
three-factor learning rules (Izhikevich 2007; Frémaux & Gerstner 2016). Here we
expose a simple multiplicative modulator; this is a deliberate simplification of
the eligibility-trace machinery those papers describe.

Simplifications
---------------
* Pair-based (nearest-neighbour via decaying traces), not triplet STDP.
* Additive weight update with hard bounds [w_min, w_max].
* Modulator applied instantaneously, without a separate eligibility trace.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class STDPConfig:
    """Configuration for pair-based STDP on an excitatory connection."""

    a_plus: float = 0.01      # potentiation learning rate (pre-before-post)
    a_minus: float = 0.012    # depression learning rate (post-before-pre)
    tau_plus: float = 20.0    # potentiation trace time constant (ms)
    tau_minus: float = 20.0   # depression trace time constant (ms)
    w_min: float = 0.0        # lower weight bound
    w_max: float = 1.0        # upper weight bound
    tau_eligibility: float | None = None
    # If set (ms), STDP changes accumulate into a decaying eligibility trace
    # instead of modifying weights immediately. Weights then change only when
    # apply_reward() is called (three-factor learning). If None, STDP is
    # applied immediately, gated by the per-step modulator.

    def __post_init__(self) -> None:
        if self.tau_plus <= 0 or self.tau_minus <= 0:
            raise ValueError("STDP time constants must be > 0")
        if self.w_max <= self.w_min:
            raise ValueError("w_max must be > w_min")
        if self.tau_eligibility is not None and self.tau_eligibility <= 0:
            raise ValueError("tau_eligibility must be > 0 when set")


class STDPSynapse:
    """Maintains STDP traces for one connection and updates its weights.

    Traces decay exponentially and are incremented on each spike:

        x_pre  tracks recent presynaptic activity (size n_pre)
        x_post tracks recent postsynaptic activity (size n_post)

    On a postsynaptic spike the weight is potentiated proportionally to the
    presynaptic trace; on a presynaptic spike it is depressed proportionally to
    the postsynaptic trace. An optional scalar ``modulator`` multiplies the net
    change to implement reward-modulated learning.
    """

    def __init__(self, n_pre: int, n_post: int, config: STDPConfig | None = None) -> None:
        self.config = config or STDPConfig()
        self.x_pre = np.zeros(n_pre, dtype=np.float64)
        self.x_post = np.zeros(n_post, dtype=np.float64)
        self.eligibility = np.zeros((n_post, n_pre), dtype=np.float64)

    def reset(self) -> None:
        self.x_pre[:] = 0.0
        self.x_post[:] = 0.0
        self.eligibility[:] = 0.0

    def clear_eligibility(self) -> None:
        """Zero the eligibility trace without touching spike traces or weights."""
        self.eligibility[:] = 0.0

    def update(
        self,
        weights: np.ndarray,
        pre_spikes: np.ndarray,
        post_spikes: np.ndarray,
        dt: float,
        modulator: float = 1.0,
    ) -> np.ndarray:
        """Decay traces, apply STDP, and return the (possibly unchanged) weights.

        ``weights`` has shape ``(n_post, n_pre)`` and is modified in place when
        STDP is in immediate mode (``tau_eligibility is None``). In eligibility
        mode the net STDP change is accumulated into ``self.eligibility`` and
        weights are left untouched until :meth:`apply_reward` is called.
        """
        c = self.config
        # Decay traces, then register this step's spikes.
        self.x_pre *= np.exp(-dt / c.tau_plus)
        self.x_post *= np.exp(-dt / c.tau_minus)
        self.x_pre[pre_spikes] += 1.0
        self.x_post[post_spikes] += 1.0

        dw = np.zeros_like(weights)
        # Potentiation: post spikes paired with recent pre activity.
        if post_spikes.any():
            dw += c.a_plus * np.outer(post_spikes.astype(np.float64), self.x_pre)
        # Depression: pre spikes paired with recent post activity.
        if pre_spikes.any():
            dw -= c.a_minus * np.outer(self.x_post, pre_spikes.astype(np.float64))

        if c.tau_eligibility is None:
            weights += modulator * dw
            np.clip(weights, c.w_min, c.w_max, out=weights)
        else:
            self.eligibility *= np.exp(-dt / c.tau_eligibility)
            self.eligibility += dw
        return weights

    def apply_reward(self, weights: np.ndarray, modulator: float) -> np.ndarray:
        """Convert accumulated eligibility into a weight change (three-factor).

        ``delta_w = modulator * eligibility`` is applied and clipped. Only
        meaningful in eligibility mode.
        """
        c = self.config
        weights += modulator * self.eligibility
        np.clip(weights, c.w_min, c.w_max, out=weights)
        return weights
