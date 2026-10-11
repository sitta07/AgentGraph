"""Unit tests for STDP: the canonical timing asymmetry and weight bounds."""

import numpy as np

from neuralmind.core.plasticity import STDPConfig, STDPSynapse


def _spike(n, idx):
    v = np.zeros(n, dtype=bool)
    v[idx] = True
    return v


def test_pre_before_post_potentiates():
    syn = STDPSynapse(1, 1, STDPConfig())
    w = np.array([[0.5]])
    dt = 1.0
    # Presynaptic spike at t=0, postsynaptic spike a few ms later.
    syn.update(w, _spike(1, 0), np.zeros(1, bool), dt)
    for _ in range(3):
        syn.update(w, np.zeros(1, bool), np.zeros(1, bool), dt)
    syn.update(w, np.zeros(1, bool), _spike(1, 0), dt)
    assert w[0, 0] > 0.5


def test_post_before_pre_depresses():
    syn = STDPSynapse(1, 1, STDPConfig())
    w = np.array([[0.5]])
    dt = 1.0
    syn.update(w, np.zeros(1, bool), _spike(1, 0), dt)
    for _ in range(3):
        syn.update(w, np.zeros(1, bool), np.zeros(1, bool), dt)
    syn.update(w, _spike(1, 0), np.zeros(1, bool), dt)
    assert w[0, 0] < 0.5


def test_weights_stay_bounded():
    cfg = STDPConfig(a_plus=0.5, a_minus=0.5, w_min=0.0, w_max=1.0)
    syn = STDPSynapse(2, 2, cfg)
    w = np.full((2, 2), 0.5)
    rng = np.random.default_rng(0)
    for _ in range(500):
        pre = rng.random(2) < 0.3
        post = rng.random(2) < 0.3
        syn.update(w, pre, post, 1.0)
    assert w.min() >= 0.0
    assert w.max() <= 1.0


def test_reward_modulator_flips_sign():
    """A negative modulator turns potentiation into depression."""
    w_pos = np.array([[0.5]])
    w_neg = np.array([[0.5]])
    syn_pos = STDPSynapse(1, 1)
    syn_neg = STDPSynapse(1, 1)
    for syn, w, mod in ((syn_pos, w_pos, 1.0), (syn_neg, w_neg, -1.0)):
        syn.update(w, _spike(1, 0), np.zeros(1, bool), 1.0, modulator=mod)
        syn.update(w, np.zeros(1, bool), _spike(1, 0), 1.0, modulator=mod)
    assert w_pos[0, 0] > 0.5
    assert w_neg[0, 0] < 0.5
