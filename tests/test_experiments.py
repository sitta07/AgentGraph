"""Behavioural tests: learning must beat a no-learning baseline."""

import pytest

from neuralmind.experiments.reward_learning import (
    RewardLearningExperiment,
    RewardLearningConfig,
)
from neuralmind.experiments.threat_avoidance import (
    ThreatAvoidanceExperiment,
    ThreatAvoidanceConfig,
)


@pytest.mark.parametrize("rewarded", [0, 1])
def test_reward_learning_beats_baseline(rewarded):
    exp = RewardLearningExperiment(RewardLearningConfig(seed=0, rewarded_action=rewarded))
    learned = exp.run(learning=True)
    baseline = exp.run(learning=False)
    # Baseline should sit near chance; learning should clearly exceed it.
    assert 0.3 <= baseline.metrics["final_selection_rate"] <= 0.7
    assert learned.metrics["final_selection_rate"] > 0.7
    assert (learned.metrics["final_selection_rate"]
            > baseline.metrics["final_selection_rate"] + 0.15)


def test_reward_learning_is_deterministic():
    cfg = RewardLearningConfig(seed=7)
    a = RewardLearningExperiment(cfg).run(learning=True)
    b = RewardLearningExperiment(cfg).run(learning=True)
    assert a.series["choice"] == b.series["choice"]


def test_threat_paired_beats_unpaired():
    exp = ThreatAvoidanceExperiment(ThreatAvoidanceConfig(seed=0))
    paired = exp.run(paired=True)
    unpaired = exp.run(paired=False)
    assert paired.metrics["associative_gain"] > 0
    assert (paired.metrics["associative_gain"]
            > unpaired.metrics["associative_gain"] + 1.0)
    # Weights should have grown in the paired case.
    assert paired.metrics["weight_mean"] > unpaired.metrics["weight_mean"]


def test_threat_affect_readout_present():
    exp = ThreatAvoidanceExperiment(ThreatAvoidanceConfig(seed=1))
    paired = exp.run(paired=True)
    assert 0.0 <= paired.metrics["affect_threat"] <= 1.0
