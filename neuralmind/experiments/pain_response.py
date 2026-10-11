"""Experiment 3: nociceptive-like input (dose-response and recovery).

Question
--------
Does a graded nociceptive-like input drive a proportional population response
and a corresponding drop in affective valence, and does activity recover after
the input stops?

IMPORTANT: this is a *sensory-signal* model. It does NOT demonstrate, and must
not be presented as, subjective pain or suffering. Status: **exploratory** (no
validated biological magnitude is claimed).

Design
------
A ``nociceptor`` population is driven for a stimulation window at a set
intensity, then released. We record the population firing rate during and after
the stimulus and feed the normalised response into :class:`AffectState` as a
``pain`` driver to read out valence/arousal/threat.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from neuralmind.affect.affect_state import AffectState
from neuralmind.core.network import SpikingNetwork
from neuralmind.core.neurons import LIFPopulation
from neuralmind.experiments.base import ExperimentResult


@dataclass
class PainResponseConfig:
    n: int = 20
    dt: float = 1.0
    baseline_ms: float = 50.0
    stim_ms: float = 100.0
    recovery_ms: float = 100.0
    intensity: float = 8.0       # nociceptive drive current during stimulation
    seed: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


class PainResponseExperiment:
    def __init__(self, config: PainResponseConfig | None = None) -> None:
        self.cfg = config or PainResponseConfig()

    def _phase_rate(self, net: SpikingNetwork, ms: float, drive: float) -> float:
        steps = int(round(ms / self.cfg.dt))
        if steps == 0:
            return 0.0
        total = 0
        for _ in range(steps):
            total += int(net.step(external={"nociceptor": drive})["nociceptor"].sum())
        return total / (self.cfg.n * steps * self.cfg.dt) * 1000.0  # Hz

    def run(self, intensity: float | None = None) -> ExperimentResult:
        c = self.cfg
        intensity = c.intensity if intensity is None else intensity
        net = SpikingNetwork(dt=c.dt)
        net.add_population("nociceptor", LIFPopulation(c.n, dt=c.dt, seed=c.seed,
                                                       randomize_initial_v=True))
        net.build()

        base_rate = self._phase_rate(net, c.baseline_ms, 0.0)
        stim_rate = self._phase_rate(net, c.stim_ms, intensity)
        recov_rate = self._phase_rate(net, c.recovery_ms, 0.0)

        affect = AffectState()
        norm = max(stim_rate, 1.0)
        for _ in range(5):
            affect.update(pain=min(1.0, stim_rate / norm))

        return ExperimentResult(
            name="pain_response",
            status="exploratory",
            config=c.as_dict() | {"intensity": intensity},
            metrics={
                "baseline_rate_hz": float(base_rate),
                "stim_rate_hz": float(stim_rate),
                "recovery_rate_hz": float(recov_rate),
                "response_gain_hz": float(stim_rate - base_rate),
                "affect_valence": float(affect.valence),
                "affect_arousal": float(affect.arousal),
            },
            series={},
            notes=[
                "Nociceptive-like SENSORY channel; NOT subjective pain.",
                "Exploratory: response should scale with intensity and recover.",
            ],
        )

    def dose_response(self, intensities) -> list[tuple[float, float]]:
        """Return (intensity, stim_rate_hz) pairs for a dose-response sweep."""
        return [(float(i), self.run(intensity=i).metrics["stim_rate_hz"])
                for i in intensities]
