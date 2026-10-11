"""Tests for the reward predictor and affect state update rules."""

import pytest

from neuralmind.affect.affect_state import AffectState
from neuralmind.affect.reward import RewardPredictor


def test_rpe_positive_when_reward_exceeds_expectation():
    p = RewardPredictor(alpha=0.5)
    assert p.prediction_error(1.0) == pytest.approx(1.0)  # V starts at 0
    p.update(1.0)                                          # V -> 0.5
    # Next identical reward is now less surprising.
    assert 0.0 < p.prediction_error(1.0) < 1.0


def test_value_converges_to_constant_reward():
    p = RewardPredictor(alpha=0.3)
    for _ in range(200):
        p.update(1.0)
    assert p.value() == pytest.approx(1.0, abs=1e-3)


def test_negative_rpe_on_omitted_reward():
    p = RewardPredictor(alpha=0.5)
    for _ in range(10):
        p.update(1.0)
    assert p.prediction_error(0.0) < 0.0


def test_reward_predictor_param_validation():
    with pytest.raises(ValueError):
        RewardPredictor(alpha=0.0)
    with pytest.raises(ValueError):
        RewardPredictor(gamma=1.0)


def test_affect_valence_tracks_rpe_sign():
    pos = AffectState()
    neg = AffectState()
    for _ in range(5):
        pos.update(rpe=0.5)
        neg.update(rpe=-0.5)
    assert pos.valence > 0 > neg.valence


def test_affect_threat_rises_and_lingers():
    a = AffectState()
    a.update(threat_cue=1.0)
    high = a.threat
    assert high > 0.5
    # Without further cues threat decays but slowly (lingers).
    for _ in range(3):
        a.update(threat_cue=0.0)
    assert 0.0 < a.threat < high


def test_affect_pain_lowers_valence_raises_threat():
    a = AffectState()
    a.update(pain=1.0)
    assert a.valence < 0
    assert a.threat > 0
    assert a.arousal > 0


def test_affect_variables_stay_bounded():
    a = AffectState()
    for _ in range(100):
        a.update(rpe=5.0, threat_cue=2.0, pain=2.0, reward_expectation=2.0)
    assert -1.0 <= a.valence <= 1.0
    assert 0.0 <= a.arousal <= 1.0
    assert 0.0 <= a.threat <= 1.0
    assert 0.0 <= a.frustration <= 1.0
    assert 0.0 <= a.motivation <= 1.0


def test_affect_frustration_from_negative_rpe():
    a = AffectState()
    for _ in range(5):
        a.update(rpe=-1.0)
    assert a.frustration > 0
