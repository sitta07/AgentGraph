"""Shared experiment result container."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ExperimentResult:
    """Structured output of an experiment run.

    Attributes
    ----------
    name:
        Experiment identifier.
    status:
        "validated" if compared against a known expected result, otherwise
        "exploratory".
    config:
        The exact configuration used (for reproducibility).
    metrics:
        Scalar summary metrics (e.g. final selection rate, learning gain).
    series:
        Named time/trial series (lists of numbers) for plotting.
    notes:
        Free-form caveats and limitations.
    """

    name: str
    status: str = "exploratory"
    config: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    series: dict[str, list] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
