"""Experiment 6: forgetting and retroactive interference.

Question
--------
If a cue population learns to drive a shared target population (memory A), and
then a *second*, overlapping cue is trained on the same target (memory B), does
recall of A degrade (retroactive interference / forgetting)?

Status: **exploratory** — a qualitative demonstration of interference in an
STDP network, not calibrated to a biological forgetting curve.

Design
------
Two cue populations (``cueA``, ``cueB``) each project via a plastic connection
to one shared ``target`` population. Training a cue = presenting that cue
together with a teaching drive to the target (Hebbian co-activation), which
potentiates that cue->target pathway. Crucially, the two memories compete for a
**bounded synaptic budget**: after each training trial, every target neuron's
total incoming weight (summed across BOTH cue pathways) is scaled back to a cap.
This homeostatic **synaptic scaling** (Turrigiano & Nelson 2004) is what makes
training B *overwrite* part of memory A. Recall = present a cue alone and count
target spikes.

Protocol: measure recall A (pre) -> train A -> recall A (post-A) -> train B ->
recall A (post-B) and recall B. Interference shows as recall-A dropping from
post-A to post-B.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFPopulation
from neuralmind.core.plasticity import STDPConfig
from neuralmind.experiments.base import ExperimentResult


@dataclass
class ForgettingConfig:
    n: int = 16
    dt: float = 1.0
    trial_ms: float = 60.0
    n_train: int = 50
    n_test: int = 15
    cue_current: float = 6.0
    teach_current: float = 12.0
    w_init: float = 0.05
    w_max: float = 1.0
    a_plus: float = 0.02
    a_minus: float = 0.01
    w_budget: float = 4.0       # max total incoming weight per target neuron
    seed: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


class ForgettingExperiment:
    def __init__(self, config: ForgettingConfig | None = None) -> None:
        self.cfg = config or ForgettingConfig()

    def _build(self) -> SpikingNetwork:
        c = self.cfg
        net = SpikingNetwork(dt=c.dt)
        for name in ("cueA", "cueB"):
            net.add_population(name, LIFPopulation(c.n, dt=c.dt))
        net.add_population("target", LIFPopulation(c.n, dt=c.dt))
        stdp = STDPConfig(a_plus=c.a_plus, a_minus=c.a_minus, w_max=c.w_max)
        for cue in ("cueA", "cueB"):
            w = np.full((c.n, c.n), c.w_init)
            net.connect(Connection(cue, "target", weights=w, tau_syn=5.0,
                                   plastic=True, stdp_config=stdp))
        net.build()
        return net

    def _steps(self) -> int:
        return int(round(self.cfg.trial_ms / self.cfg.dt))

    def _recall(self, net: SpikingNetwork, cue: str) -> float:
        """Present a cue alone with plasticity frozen; return mean target spikes."""
        frozen = [(cn, cn.plastic) for cn in net.connections]
        for cn in net.connections:
            cn.plastic = False
        totals = []
        for _ in range(self.cfg.n_test):
            net.reset()
            t = 0
            for _ in range(self._steps()):
                t += int(net.step(external={cue: self.cfg.cue_current})["target"].sum())
            totals.append(t)
        for cn, was in frozen:
            cn.plastic = was
        return float(np.mean(totals))

    def _scale(self, net: SpikingNetwork) -> None:
        """Homeostatic synaptic scaling: cap total incoming weight per target neuron.

        Sums each target neuron's incoming weights across both cue pathways; if
        the row total exceeds ``w_budget``, all its incoming weights are scaled
        down proportionally. This makes the two memories compete for a shared,
        bounded synaptic resource (Turrigiano & Nelson 2004).
        """
        conns = net.connections  # [cueA->target, cueB->target]
        totals = sum(c.weights.sum(axis=1) for c in conns)  # per target neuron
        over = totals > self.cfg.w_budget
        if over.any():
            factor = np.ones_like(totals)
            factor[over] = self.cfg.w_budget / totals[over]
            for c in conns:
                c.weights *= factor[:, None]

    def _train(self, net: SpikingNetwork, cue: str) -> None:
        for _ in range(self.cfg.n_train):
            net.reset()
            for _ in range(self._steps()):
                net.step(external={cue: self.cfg.cue_current,
                                   "target": self.cfg.teach_current},
                         modulator=1.0)
            self._scale(net)

    def run(self) -> ExperimentResult:
        net = self._build()
        recall_a_pre = self._recall(net, "cueA")
        self._train(net, "cueA")
        recall_a_postA = self._recall(net, "cueA")
        self._train(net, "cueB")
        recall_a_postB = self._recall(net, "cueA")
        recall_b_postB = self._recall(net, "cueB")

        interference = recall_a_postA - recall_a_postB
        return ExperimentResult(
            name="forgetting",
            status="exploratory",
            config=self.cfg.as_dict(),
            metrics={
                "recall_A_pre": recall_a_pre,
                "recall_A_after_A": recall_a_postA,
                "recall_A_after_B": recall_a_postB,
                "recall_B_after_B": recall_b_postB,
                "interference_drop": float(interference),
            },
            series={},
            notes=[
                "Retroactive interference: training B overwrites memory A because",
                "the shared synaptic budget is reallocated to the B pathway.",
                "This minimal setup shows (near-)CATASTROPHIC interference, a known",
                "failure mode; biological systems add consolidation/replay to resist it.",
                "Exploratory; qualitative, not calibrated to a forgetting curve.",
            ],
        )
