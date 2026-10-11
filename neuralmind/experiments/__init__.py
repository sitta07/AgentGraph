"""Reproducible experiments built on the neural simulation core.

Each experiment exposes documented parameters, runs deterministically from a
seed, and returns an :class:`ExperimentResult` with per-trial metrics and
traces. Experiments that lack a validated biological expected value are labelled
*exploratory* rather than *validated*.
"""

from neuralmind.experiments.base import ExperimentResult
from neuralmind.experiments.reward_learning import (
    RewardLearningExperiment,
    RewardLearningConfig,
)
from neuralmind.experiments.threat_avoidance import (
    ThreatAvoidanceExperiment,
    ThreatAvoidanceConfig,
)

__all__ = [
    "ExperimentResult",
    "RewardLearningExperiment",
    "RewardLearningConfig",
    "ThreatAvoidanceExperiment",
    "ThreatAvoidanceConfig",
]
