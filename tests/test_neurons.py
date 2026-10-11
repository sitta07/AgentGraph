"""Unit tests for the LIF neuron population and its documented dynamics."""

import numpy as np
import pytest

from neuralmind.core.neurons import LIFParams, LIFPopulation


def test_rest_stays_at_rest_without_input():
    pop = LIFPopulation(10, dt=1.0)
    for _ in range(100):
        spikes = pop.step(0.0)
        assert not spikes.any()
    assert np.allclose(pop.v, pop.params.v_rest)


def test_subthreshold_input_does_not_spike():
    # Steady-state V = v_rest + R*I. Keep it just below threshold.
    p = LIFParams()
    i_sub = (p.v_threshold - p.v_rest) / p.r_m * 0.9
    pop = LIFPopulation(5, p, dt=1.0)
    fired = False
    for _ in range(500):
        fired = fired or pop.step(i_sub).any()
    assert not fired
    assert np.all(pop.v < p.v_threshold)


def test_suprathreshold_input_spikes_and_resets():
    p = LIFParams()
    i_sup = (p.v_threshold - p.v_rest) / p.r_m * 2.0
    pop = LIFPopulation(1, p, dt=1.0)
    spike_count = sum(int(pop.step(i_sup)[0]) for _ in range(200))
    assert spike_count > 0
    # After any spike the neuron must have been reset at least once.
    assert pop.v[0] <= p.v_threshold


def test_refractory_period_limits_rate():
    p = LIFParams(refractory=10.0)
    i_huge = 100.0
    pop = LIFPopulation(1, p, dt=1.0)
    spike_count = sum(int(pop.step(i_huge)[0]) for _ in range(1000))
    # With 10 ms refractory over 1000 ms, firing cannot exceed ~100 spikes.
    assert spike_count <= 1000 / p.refractory + 1


def test_fi_curve_is_monotonic():
    """Firing rate should not decrease as input current increases."""
    p = LIFParams()
    rates = []
    for scale in (1.1, 1.5, 2.0, 4.0):
        i = (p.v_threshold - p.v_rest) / p.r_m * scale
        pop = LIFPopulation(1, p, dt=0.5)
        rate = sum(int(pop.step(i)[0]) for _ in range(2000))
        rates.append(rate)
    assert rates == sorted(rates)
    assert rates[-1] > rates[0]


def test_determinism_with_seed():
    def run():
        pop = LIFPopulation(20, dt=1.0, seed=42, randomize_initial_v=True)
        out = []
        for _ in range(50):
            out.append(pop.step(2.5).copy())
        return np.array(out)

    assert np.array_equal(run(), run())


def test_stability_guard():
    with pytest.raises(ValueError):
        LIFPopulation(1, LIFParams(tau_m=5.0), dt=10.0)


def test_invalid_params_rejected():
    with pytest.raises(ValueError):
        LIFParams(tau_m=-1.0)
    with pytest.raises(ValueError):
        LIFParams(v_threshold=-70.0, v_reset=-65.0)
    with pytest.raises(ValueError):
        LIFPopulation(0)


def test_input_shape_validation():
    pop = LIFPopulation(4)
    with pytest.raises(ValueError):
        pop.step(np.zeros(3))
