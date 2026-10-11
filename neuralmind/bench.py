"""Benchmark harness: measured runtime and memory for the simulation core.

Reports *actual* wall-clock time and peak memory (via ``tracemalloc``) for a
recurrent random spiking network at several sizes. Numbers are machine- and
load-dependent; they are measurements, not guarantees.

Usage
-----
    python -m neuralmind.bench
    python -m neuralmind.bench --sizes 50 100 200 --steps 500
"""

from __future__ import annotations

import argparse
import time
import tracemalloc

import numpy as np

from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFPopulation


def build_random_network(n: int, dt: float, seed: int, p_connect: float = 0.1,
                         plastic: bool = False) -> SpikingNetwork:
    """One population recurrently connected to itself with sparse random weights."""
    rng = np.random.default_rng(seed)
    net = SpikingNetwork(dt=dt)
    net.add_population("pop", LIFPopulation(n, dt=dt, seed=seed, randomize_initial_v=True))
    mask = rng.random((n, n)) < p_connect
    np.fill_diagonal(mask, False)
    weights = np.where(mask, rng.uniform(0.0, 0.5, size=(n, n)), 0.0)
    net.connect(Connection("pop", "pop", weights=weights, tau_syn=5.0, plastic=plastic))
    net.build()
    return net


def benchmark(n: int, steps: int, dt: float = 1.0, seed: int = 0,
              plastic: bool = False, drive: float = 3.0) -> dict:
    net = build_random_network(n, dt, seed, plastic=plastic)
    n_syn = int(np.count_nonzero(net.connections[0].weights))

    tracemalloc.start()
    t0 = time.perf_counter()
    total_spikes = 0
    for _ in range(steps):
        s = net.step(external={"pop": drive}, modulator=1.0)
        total_spikes += int(s["pop"].sum())
    wall = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "n_neurons": n,
        "n_synapses": n_syn,
        "steps": steps,
        "plastic": plastic,
        "wall_s": round(wall, 4),
        "steps_per_s": round(steps / wall, 1) if wall > 0 else float("inf"),
        "neuron_step_updates_per_s": round(n * steps / wall, 0) if wall > 0 else float("inf"),
        "mean_rate_hz": round(total_spikes / (n * steps * dt) * 1000.0, 2),
        "peak_mem_mb": round(peak / 1e6, 2),
    }


def run(sizes: list[int], steps: int, plastic: bool = False) -> list[dict]:
    results = []
    for n in sizes:
        r = benchmark(n, steps, plastic=plastic)
        results.append(r)
        print(
            f"n={r['n_neurons']:5d} syn={r['n_synapses']:7d} "
            f"steps={r['steps']:5d} wall={r['wall_s']:7.3f}s "
            f"{r['steps_per_s']:8.1f} steps/s  "
            f"rate={r['mean_rate_hz']:6.2f}Hz  peak={r['peak_mem_mb']:7.2f}MB"
            f"{'  [plastic]' if r['plastic'] else ''}"
        )
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sizes", type=int, nargs="+", default=[50, 100, 200, 400])
    p.add_argument("--steps", type=int, default=500)
    p.add_argument("--plastic", action="store_true", help="enable STDP (slower)")
    args = p.parse_args(argv)
    run(args.sizes, args.steps, plastic=args.plastic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
