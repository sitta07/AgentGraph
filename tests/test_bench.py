"""Smoke test for the benchmark harness."""

from neuralmind.bench import benchmark, build_random_network


def test_build_random_network_shapes():
    net = build_random_network(n=30, dt=1.0, seed=0)
    conn = net.connections[0]
    assert conn.weights.shape == (30, 30)
    # No self-connections.
    import numpy as np
    assert np.all(np.diag(conn.weights) == 0.0)


def test_benchmark_reports_measurements():
    r = benchmark(n=40, steps=50, seed=0)
    assert r["n_neurons"] == 40
    assert r["steps"] == 50
    assert r["wall_s"] >= 0.0
    assert r["peak_mem_mb"] >= 0.0
    assert r["mean_rate_hz"] >= 0.0
