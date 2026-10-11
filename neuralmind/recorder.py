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
    # Optional 3-D network layout (for the brain-style viewer).
    # nodes[i] = {"p": population_name, "x","y","z": coords in [-1, 1]}.
    nodes: list[dict] = field(default_factory=list)
    # edges[k] = {"s": src_global_idx, "t": dst_global_idx, "w": weight}.
    edges: list[dict] = field(default_factory=list)
    # matrix = NxN signed connectivity (row=post, col=pre), for the heatmap.
    matrix: list[list[float]] = field(default_factory=list)
    # activity[step] = per-node decaying activation in [0, 1] (spike "glow").
    activity: list[list[float]] = field(default_factory=list)

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
            "nodes": self.nodes,
            "edges": self.edges,
            "matrix": self.matrix,
            "activity": self.activity,
            "n_steps": self.n_steps,
        }


def build_layout(net: SpikingNetwork, seed: int = 0, max_edges: int = 700) -> dict:
    """Assign 3-D coordinates to every neuron and extract edges + a matrix.

    Neurons are scattered inside a brain-like ellipsoid, each population in its
    own sub-region so groups are visually separable. Edges and the NxN signed
    connectivity matrix are read directly from the network's weight matrices.
    """
    rng = np.random.default_rng(seed)
    pops = list(net.populations)
    offset, offsets = 0, {}
    nodes: list[dict] = []
    # Spread population centres along x so groups don't overlap.
    centres = np.linspace(-0.55, 0.55, len(pops)) if len(pops) > 1 else [0.0]
    for pi, p in enumerate(pops):
        offsets[p] = offset
        n = net.populations[p].n
        cx = float(centres[pi])
        for _ in range(n):
            # Point inside an ellipsoid shell around the population centre.
            v = rng.normal(size=3)
            v /= np.linalg.norm(v) or 1.0
            r = 0.30 * rng.uniform(0.35, 1.0) ** (1 / 3)
            nodes.append({
                "p": p,
                "x": round(cx + v[0] * r * 1.1, 4),
                "y": round(v[1] * r * 1.3, 4),
                "z": round(v[2] * r * 1.0, 4),
            })
        offset += n

    total = offset
    matrix = [[0.0] * total for _ in range(total)]
    edges: list[dict] = []
    for c in net.connections:
        w = c.weights
        po, pre_o = offsets[c.post], offsets[c.pre]
        for i in range(w.shape[0]):
            gi = po + i
            for j in range(w.shape[1]):
                val = float(w[i, j])
                if val == 0.0:
                    continue
                gj = pre_o + j
                matrix[gi][gj] += round(val, 4)
                edges.append({"s": gj, "t": gi, "w": round(val, 4)})

    # Keep the strongest edges only, for render performance.
    edges.sort(key=lambda e: abs(e["w"]), reverse=True)
    edges = edges[:max_edges]
    return {"nodes": nodes, "edges": edges, "matrix": matrix, "offsets": offsets,
            "total": total}


def record(
    net: SpikingNetwork,
    steps: int,
    external: Callable[[int], dict] | dict | None = None,
    modulator: Callable[[int], float] | float = 1.0,
    extra_series: Callable[[int], dict] | None = None,
    meta: dict | None = None,
    layout: bool = False,
    layout_seed: int = 0,
    activity_tau: float = 15.0,
) -> Recording:
    """Step ``net`` for ``steps`` steps, recording spikes, rates and series.

    ``external`` may be a fixed dict or a function of the step index; likewise
    ``modulator``. ``extra_series`` optionally returns a dict of scalar values
    to record each step (e.g. affect variables). When ``layout`` is true, a 3-D
    node layout, edges, connectivity matrix, and a per-node decaying activity
    trace are captured for the brain-style viewer.
    """
    if not net._built:
        net.build()
    pops = list(net.populations)
    sizes = {p: net.populations[p].n for p in pops}
    rec = Recording(dt=net.dt, populations=pops, sizes=sizes, meta=meta or {})
    for p in pops:
        rec.spikes[p] = []
        rec.rate[p] = []

    lay = None
    glow = None
    decay = float(np.exp(-net.dt / activity_tau))
    if layout:
        lay = build_layout(net, seed=layout_seed)
        rec.nodes, rec.edges, rec.matrix = lay["nodes"], lay["edges"], lay["matrix"]
        glow = np.zeros(lay["total"], dtype=np.float64)

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
        if glow is not None:
            glow *= decay
            for p in pops:
                g = lay["offsets"][p]
                glow[g:g + sizes[p]] = np.maximum(glow[g:g + sizes[p]], spikes[p])
            rec.activity.append([round(float(x), 3) for x in glow])
    return rec
