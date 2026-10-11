"""Record the actual state of a running :class:`SpikingNetwork` for inspection.

Everything captured here comes from real simulation steps — spike vectors,
population firing rates, and optional scalar series supplied by the caller. The
visualization layer (:mod:`neuralmind.viz`) renders only what is recorded here,
so what a viewer sees corresponds to actual simulation state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from neuralmind.core.network import SpikingNetwork


@dataclass
class Recording:
    dt: float
    populations: list[str]
    sizes: dict[str, int]
    # spikes[pop] = list over steps of the indices that fired that step.
    spikes: dict[str, list[list[int]]] = field(default_factory=dict)
    # rate[pop] = list over steps of instantaneous population rate (Hz).
    rate: dict[str, list[float]] = field(default_factory=dict)
    # extra named scalar series over steps (e.g. affect variables).
    series: dict[str, list[float]] = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    @property
    def n_steps(self) -> int:
        any_pop = next(iter(self.spikes), None)
        return len(self.spikes[any_pop]) if any_pop else 0

    def to_json_dict(self) -> dict:
        return {
            "dt": self.dt,
            "populations": self.populations,
            "sizes": self.sizes,
            "spikes": self.spikes,
            "rate": self.rate,
            "series": self.series,
            "meta": self.meta,
            "n_steps": self.n_steps,
        }


def record(
    net: SpikingNetwork,
    steps: int,
    external: Callable[[int], dict] | dict | None = None,
    modulator: Callable[[int], float] | float = 1.0,
    extra_series: Callable[[int], dict] | None = None,
    meta: dict | None = None,
) -> Recording:
    """Step ``net`` for ``steps`` steps, recording spikes, rates and series.

    ``external`` may be a fixed dict or a function of the step index; likewise
    ``modulator``. ``extra_series`` optionally returns a dict of scalar values
    to record each step (e.g. affect variables).
    """
    if not net._built:
        net.build()
    pops = list(net.populations)
    sizes = {p: net.populations[p].n for p in pops}
    rec = Recording(dt=net.dt, populations=pops, sizes=sizes, meta=meta or {})
    for p in pops:
        rec.spikes[p] = []
        rec.rate[p] = []

    for i in range(steps):
        ext = external(i) if callable(external) else external
        mod = modulator(i) if callable(modulator) else modulator
        spikes = net.step(external=ext, modulator=mod)
        for p in pops:
            idx = np.nonzero(spikes[p])[0].tolist()
            rec.spikes[p].append(idx)
            rec.rate[p].append(round(len(idx) / sizes[p] / net.dt * 1000.0, 2))
        if extra_series is not None:
            for k, v in extra_series(i).items():
                rec.series.setdefault(k, []).append(round(float(v), 4))
    return rec
