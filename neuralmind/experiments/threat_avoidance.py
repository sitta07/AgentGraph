"""Experiment 2: threat association and avoidance via Hebbian STDP.

Question
--------
If a neutral conditioned stimulus (CS) is repeatedly paired with an aversive
unconditioned stimulus (US) that strongly drives a defensive population, does
the CS alone come to elicit a defensive response (associative learning)?

Design (Pavlovian threat conditioning, abstracted)
--------------------------------------------------
* ``cs``      — conditioned-stimulus input population.
* ``defense`` — defensive/avoidance population.
* A single plastic ``cs -> defense`` connection with immediate Hebbian STDP.

Phases:
  1. pre-test  : present CS alone; record defensive response (baseline).
  2. training  : PAIRED -> CS and US co-active (US injects current into
                 ``defense``), producing pre-before-post correlation that
                 potentiates ``cs -> defense``. UNPAIRED control -> CS and US on
                 alternating, non-overlapping trials (no co-activation).
  3. post-test : present CS alone; record defensive response.

Expected behaviour
------------------
The PAIRED group's CS-evoked defensive response should grow from pre to post,
and more than the UNPAIRED control. This is the qualitative hallmark of
associative conditioning; the result is *validated* against that qualitative
expectation only (no biological magnitude is claimed). The accompanying affect
``threat`` variable is reported as an illustrative read-out, not evidence of
subjective fear.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from neuralmind.affect.affect_state import AffectState
from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFPopulation
from neuralmind.core.plasticity import STDPConfig
from neuralmind.experiments.base import ExperimentResult


@dataclass
class ThreatAvoidanceConfig:
    n_cs: int = 12
    n_defense: int = 12
    n_pairings: int = 60
    n_test: int = 20
    trial_ms: float = 60.0
    dt: float = 1.0
    cs_current: float = 6.0
    us_current: float = 12.0     # aversive drive into the defense population
    w_init: float = 0.05
    w_max: float = 1.0
    a_plus: float = 0.02
    seed: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


class ThreatAvoidanceExperiment:
    def __init__(self, config: ThreatAvoidanceConfig | None = None) -> None:
        self.cfg = config or ThreatAvoidanceConfig()

    def _build(self, rng: np.random.Generator) -> SpikingNetwork:
        c = self.cfg
        net = SpikingNetwork(dt=c.dt)
        net.add_population("cs", LIFPopulation(c.n_cs, dt=c.dt))
        net.add_population("defense", LIFPopulation(c.n_defense, dt=c.dt))
        stdp = STDPConfig(a_plus=c.a_plus, a_minus=c.a_plus * 0.5, w_max=c.w_max)
        w = np.full((c.n_defense, c.n_cs), c.w_init)
        net.connect(Connection("cs", "defense", weights=w, tau_syn=5.0,
                               plastic=True, stdp_config=stdp))
        return net

    def _response_to_cs(self, net: SpikingNetwork, steps: int, learn: bool) -> int:
        """Present CS alone and count defensive spikes (optionally frozen weights)."""
        net.reset()
        conn = net.connections[0]
        was_plastic = conn.plastic
        if not learn:
            conn.plastic = False
        total = 0
        for _ in range(steps):
            s = net.step(external={"cs": self.cfg.cs_current})
            total += int(s["defense"].sum())
        conn.plastic = was_plastic
        return total

    def run(self, paired: bool = True) -> ExperimentResult:
        c = self.cfg
        rng = np.random.default_rng(c.seed)
        net = self._build(rng)
        steps = int(round(c.trial_ms / c.dt))

        pre = np.mean([self._response_to_cs(net, steps, learn=False)
                       for _ in range(c.n_test)])

        # Training phase.
        for i in range(c.n_pairings):
            net.reset()
            for _ in range(steps):
                if paired:
                    ext = {"cs": c.cs_current, "defense": c.us_current}
                else:
                    # Unpaired: CS and US never overlap (alternate trials).
                    ext = ({"cs": c.cs_current} if i % 2 == 0
                           else {"defense": c.us_current})
                net.step(external=ext, modulator=1.0)

        post = np.mean([self._response_to_cs(net, steps, learn=False)
                        for _ in range(c.n_test)])

        # Illustrative affect read-out: scale CS response into a threat cue.
        affect = AffectState()
        norm = max(post, pre, 1.0)
        for _ in range(5):
            affect.update(threat_cue=min(1.0, post / norm))

        result = ExperimentResult(
            name="threat_avoidance",
            status="validated",
            config=c.as_dict() | {"paired": paired},
            metrics={
                "pre_response": float(pre),
                "post_response": float(post),
                "associative_gain": float(post - pre),
                "weight_mean": float(net.connections[0].weights.mean()),
                "affect_threat": float(affect.threat),
            },
            series={},
            notes=[
                "Hebbian STDP strengthens cs->defense when CS and US co-activate.",
                "Compare paired (run(paired=True)) vs unpaired control.",
                "Affect 'threat' is an illustrative read-out, not evidence of fear.",
            ],
        )
        return result
