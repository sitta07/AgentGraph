"""Tests for the pain-response and forgetting experiments (exploratory)."""

import pytest

from neuralmind.experiments.pain_response import (
    PainResponseConfig,
    PainResponseExperiment,
)
from neuralmind.experiments.forgetting import (
    ForgettingConfig,
    ForgettingExperiment,
)


def test_pain_dose_response_is_monotonic():
    exp = PainResponseExperiment(PainResponseConfig(seed=0))
    pairs = exp.dose_response([0, 2, 4, 8])
    rates = [r for _, r in pairs]
    assert rates == sorted(rates)
    assert rates[0] == 0.0          # no drive -> no spikes
    assert rates[-1] > rates[0]


def test_pain_recovers_and_lowers_valence():
    r = PainResponseExperiment(PainResponseConfig(seed=0)).run()
    m = r.metrics
    assert m["stim_rate_hz"] > m["baseline_rate_hz"]
    assert m["recovery_rate_hz"] < m["stim_rate_hz"]   # activity recovers
    assert m["affect_valence"] < 0                      # unpleasant read-out
    assert r.status == "exploratory"


def test_pain_is_labelled_not_subjective():
    r = PainResponseExperiment().run()
    assert any("NOT subjective pain" in n for n in r.notes)


def test_forgetting_shows_retroactive_interference():
    r = ForgettingExperiment(ForgettingConfig(seed=0)).run()
    m = r.metrics
    # A must first be learned above its pre-training recall.
    assert m["recall_A_after_A"] > m["recall_A_pre"]
    # Training B must reduce recall of A (interference).
    assert m["recall_A_after_B"] < m["recall_A_after_A"]
    assert m["interference_drop"] > 0
    # B itself is retained.
    assert m["recall_B_after_B"] > 0


def test_forgetting_deterministic():
    a = ForgettingExperiment(ForgettingConfig(seed=3)).run().metrics
    b = ForgettingExperiment(ForgettingConfig(seed=3)).run().metrics
    assert a == b
