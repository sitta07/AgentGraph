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
