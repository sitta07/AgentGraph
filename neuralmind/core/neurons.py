"""Leaky integrate-and-fire (LIF) neuron populations.

Scientific basis
----------------
The leaky integrate-and-fire neuron is a classic, well-validated reduced model
of a spiking neuron (Lapicque 1907; Tuckwell 1988; Gerstner & Kistler 2002,
*Spiking Neuron Models*). The subthreshold membrane potential V obeys

    tau_m * dV/dt = -(V - V_rest) + R * I(t)

When V crosses the threshold V_th a spike is emitted, V is clamped to V_reset,
and the neuron is held at V_reset for an absolute refractory period.

Simplifications (engineering approximations, NOT biological claims)
-------------------------------------------------------------------
* Point neuron: no dendritic morphology, no spatial structure.
* Current-based input (we inject a current I); no explicit ion channels.
* Fixed hard threshold; no adaptation or sub-threshold resonance by default.
* Forward-Euler integration. Accurate for dt << tau_m; we test stability.

Units
-----
Voltages in millivolts (mV), time in milliseconds (ms), resistance in
megaohms (MOhm), current in nanoamperes (nA) so that R * I has units of mV.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LIFParams:
    """Parameters for a homogeneous LIF population.

    Defaults are biologically plausible cortical-neuron values but are a
    modelling choice, not a measurement of any specific cell.
    """

    tau_m: float = 20.0       # membrane time constant (ms)
    v_rest: float = -65.0     # resting potential (mV)
    v_reset: float = -65.0    # reset potential after a spike (mV)
    v_threshold: float = -50.0  # spike threshold (mV)
    r_m: float = 10.0         # membrane resistance (MOhm)
    refractory: float = 5.0   # absolute refractory period (ms)

    def __post_init__(self) -> None:
        if self.tau_m <= 0:
            raise ValueError("tau_m must be > 0")
        if self.r_m <= 0:
            raise ValueError("r_m must be > 0")
        if self.refractory < 0:
            raise ValueError("refractory must be >= 0")
        if self.v_threshold <= self.v_reset:
            raise ValueError("v_threshold must be > v_reset")


class LIFPopulation:
    """A vectorised population of independent LIF neurons.

    State is held in NumPy arrays of shape ``(n,)``. The population is
    deterministic given a seed: it only draws randomness for the optional
    membrane-potential initialisation.
    """

    def __init__(
        self,
        n: int,
        params: LIFParams | None = None,
        *,
        dt: float = 1.0,
        seed: int | None = None,
        randomize_initial_v: bool = False,
    ) -> None:
        if n <= 0:
            raise ValueError("n must be >= 1")
        if dt <= 0:
            raise ValueError("dt must be > 0")
        self.n = int(n)
        self.params = params or LIFParams()
        self.dt = float(dt)
        self._rng = np.random.default_rng(seed)

        # Stability guard for forward Euler on the membrane equation.
        if self.dt > self.params.tau_m:
            raise ValueError(
                f"dt ({self.dt} ms) must be <= tau_m ({self.params.tau_m} ms) "
                "for a stable forward-Euler membrane update"
            )

        self.v = np.full(self.n, self.params.v_rest, dtype=np.float64)
        if randomize_initial_v:
            span = self.params.v_threshold - self.params.v_rest
            self.v += self._rng.uniform(0.0, span, size=self.n)

        # Remaining refractory time per neuron, in ms.
        self.refractory_left = np.zeros(self.n, dtype=np.float64)
        self.spikes = np.zeros(self.n, dtype=bool)
        self.t = 0.0

    def reset(self) -> None:
        """Reset membrane state and time (keeps the RNG stream position)."""
        self.v[:] = self.params.v_rest
        self.refractory_left[:] = 0.0
        self.spikes[:] = False
        self.t = 0.0

    def step(self, input_current: np.ndarray | float) -> np.ndarray:
        """Advance the population by one time step.

        Parameters
        ----------
        input_current:
            Injected current per neuron (nA), scalar or shape ``(n,)``.

        Returns
        -------
        np.ndarray
            Boolean spike vector of shape ``(n,)`` for this step.
        """
        p = self.params
        i = np.asarray(input_current, dtype=np.float64)
        if i.ndim == 0:
            i = np.full(self.n, float(i))
        elif i.shape != (self.n,):
            raise ValueError(
                f"input_current must be scalar or shape ({self.n},), got {i.shape}"
            )

        active = self.refractory_left <= 0.0

        # Forward-Euler update only for non-refractory neurons.
        dv = (self.dt / p.tau_m) * (-(self.v - p.v_rest) + p.r_m * i)
        self.v = np.where(active, self.v + dv, p.v_reset)

        # Detect spikes.
        spiked = active & (self.v >= p.v_threshold)
        self.v = np.where(spiked, p.v_reset, self.v)
        self.refractory_left = np.where(
            spiked, p.refractory, np.maximum(0.0, self.refractory_left - self.dt)
        )

        self.spikes = spiked
        self.t += self.dt
        return spiked

    def state(self) -> dict:
        """Return a copy of the current observable state."""
        return {
            "t": self.t,
            "v": self.v.copy(),
            "spikes": self.spikes.copy(),
            "refractory_left": self.refractory_left.copy(),
        }
