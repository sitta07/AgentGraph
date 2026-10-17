"""Unit tests for the SpikingNetwork wiring, transmission, and determinism."""

import numpy as np
import pytest

from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFParams, LIFPopulation


def _net(dt=1.0, plastic=False):
    net = SpikingNetwork(dt=dt)
    net.add_population("A", LIFPopulation(2, dt=dt))
    net.add_population("B", LIFPopulation(2, dt=dt))
    net.connect(Connection("A", "B", weights=np.zeros((2, 2)), plastic=plastic))
    return net


def test_dt_mismatch_rejected():
    net = SpikingNetwork(dt=1.0)
    with pytest.raises(ValueError):
        net.add_population("A", LIFPopulation(1, dt=0.5))


def test_weight_shape_validation():
    net = SpikingNetwork(dt=1.0)
    net.add_population("A", LIFPopulation(2))
    net.add_population("B", LIFPopulation(3))
    net.connect(Connection("A", "B", weights=np.zeros((2, 2))))  # wrong shape
    with pytest.raises(ValueError):
        net.build()


def test_unknown_population_rejected():
    net = SpikingNetwork()
    net.add_population("A", LIFPopulation(1))
    with pytest.raises(ValueError):
        net.connect(Connection("A", "ghost", weights=np.zeros((1, 1))))


def test_transmission_drives_postsynaptic_spikes():
    """Strong input to A should, via synapses, make B fire."""
    dt = 1.0
    net = SpikingNetwork(dt=dt)
    net.add_population("A", LIFPopulation(1, dt=dt))
    net.add_population("B", LIFPopulation(1, dt=dt))
    # Big synaptic weight so each A spike strongly drives B.
    net.connect(Connection("A", "B", weights=np.array([[50.0]]), tau_syn=5.0))

    a_spikes = b_spikes = 0
    for _ in range(300):
        s = net.step(external={"A": 5.0})
        a_spikes += int(s["A"][0])
        b_spikes += int(s["B"][0])
    assert a_spikes > 0
    assert b_spikes > 0


def test_isolated_population_stays_silent():
    net = _net()
    for _ in range(100):
        s = net.step()  # no external input, zero weights
        assert not s["A"].any() and not s["B"].any()


def test_network_determinism():
    def run():
        net = SpikingNetwork(dt=1.0)
        net.add_population("A", LIFPopulation(3, dt=1.0, seed=1, randomize_initial_v=True))
        net.add_population("B", LIFPopulation(3, dt=1.0, seed=2, randomize_initial_v=True))
        net.connect(Connection("A", "B", weights=np.full((3, 3), 10.0)))
        out = []
        for _ in range(60):
            out.append(np.concatenate(list(net.step({"A": 3.0}).values())))
        return np.array(out)

    assert np.array_equal(run(), run())


def test_reset_restores_initial_behaviour():
    net = _net()
    first = [net.step({"A": 5.0}) for _ in range(20)]
    net.reset()
    second = [net.step({"A": 5.0}) for _ in range(20)]
    for a, b in zip(first, second):
        assert np.array_equal(a["A"], b["A"])
        assert np.array_equal(a["B"], b["B"])


def _mixed_net(seed):
    from neuralmind.core.plasticity import STDPConfig
    rng = np.random.default_rng(seed)
    net = SpikingNetwork(dt=1.0)
    for name, n in (("in", 5), ("a", 4), ("b", 4), ("c", 3)):
        net.add_population(name, LIFPopulation(n, dt=1.0))
    elig = STDPConfig(a_plus=0.02, a_minus=0.0, w_max=4.0, tau_eligibility=100.0)
    for post in ("a", "b", "c"):
        n = net.populations[post].n
        net.connect(Connection("in", post, weights=rng.uniform(0.5, 2.5, (n, 5)), plastic=True, stdp_config=elig))
    net.connect(Connection("a", "b", weights=rng.uniform(0, 1, (4, 4)), plastic=True,
                           stdp_config=STDPConfig(w_max=2.0)))
    for pre, post in (("a", "c"), ("b", "a"), ("c", "b"), ("b", "c")):
        net.connect(Connection(pre, post, weights=-rng.uniform(0, 1, (net.populations[post].n, net.populations[pre].n)),
                               tau_syn=10.0))
    net.build()
    return net


def _drive(net, seed, steps, rebind_at=None):
    rng = np.random.default_rng(seed + 1)
    out = []
    for t in range(steps):
        if t == rebind_at:
            net.connections[0].weights = net.connections[0].weights.copy()
        if t % 50 == 49:
            net.apply_reward(rng.normal())
            net.clear_eligibility()
        if t == 120:
            net.reset()
        s = net.step(external={"in": rng.uniform(0, 4, 5), "a": rng.normal(0, 2, 4)})
        out.append(np.concatenate([s[k] for k in net.populations]))
    return np.array(out), [c.weights.copy() for c in net.connections]


def test_fused_step_is_bit_identical_to_the_per_object_step(monkeypatch):
    from neuralmind.core import network
    fused = _mixed_net(3)
    assert fused._fused is not None
    monkeypatch.setattr(network._Fused, "try_build", classmethod(lambda cls, net: None))
    plain = _mixed_net(3)
    assert plain._fused is None
    s1, w1 = _drive(fused, 3, 300)
    s2, w2 = _drive(plain, 3, 300)
    assert s1.any() and np.array_equal(s1, s2)
    assert all(np.array_equal(a, b) for a, b in zip(w1, w2))


def test_rebinding_an_array_after_build_falls_back_without_changing_results(monkeypatch):
    from neuralmind.core import network
    fused = _mixed_net(4)
    s1, w1 = _drive(fused, 4, 200, rebind_at=77)
    assert fused._fused is None
    monkeypatch.setattr(network._Fused, "try_build", classmethod(lambda cls, net: None))
    s2, w2 = _drive(_mixed_net(4), 4, 200, rebind_at=77)
    assert np.array_equal(s1, s2) and all(np.array_equal(a, b) for a, b in zip(w1, w2))
