"""A low-dimensional affect/motivation state with explicit update rules.

Scientific basis
----------------
The core-affect / circumplex model represents affect in a 2-D space of
**valence** (pleasant<->unpleasant) and **arousal** (calm<->activated)
(Russell 1980; Posner, Russell & Peterson 2005). We add three motivational
variables commonly used in computational affective models:

* **threat**   — a fast-rising, slowly-decaying defensive signal, loosely
                 inspired by amygdala-mediated threat processing (LeDoux 2000).
* **frustration** — accumulates from negative reward prediction error
                 (blocked/omitted reward; Amsel 1992).
* **motivation** — approach drive scaled by expected reward and arousal.

All variables are bounded and updated by leaky-integrator rules each tick. Units
are dimensionless model quantities on fixed ranges.

IMPORTANT: these are engineering constructs for experimentation. They do NOT
measure, and must not be presented as, subjective human feelings.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


@dataclass(frozen=True)
class AffectParams:
    """Time constants (in ticks) and gains for the affect update rules."""

    valence_decay: float = 0.9      # per-tick retention toward 0
    arousal_decay: float = 0.85
    threat_rise: float = 0.6        # fraction of gap closed on a threat cue
    threat_decay: float = 0.95      # slow decay (threat lingers)
    frustration_gain: float = 0.5   # from negative RPE
    frustration_decay: float = 0.9
    rpe_to_valence: float = 0.5     # how strongly RPE shifts valence

    def __post_init__(self) -> None:
        for name in ("valence_decay", "arousal_decay", "threat_decay", "frustration_decay"):
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass
class AffectState:
    """Mutable affect state, updated one discrete tick at a time."""

    valence: float = 0.0       # [-1, 1]
    arousal: float = 0.0       # [0, 1]
    threat: float = 0.0        # [0, 1]
    frustration: float = 0.0   # [0, 1]
    motivation: float = 0.0    # [0, 1]
    params: AffectParams = None

    def __post_init__(self) -> None:
        if self.params is None:
            self.params = AffectParams()

    def update(
        self,
        *,
        rpe: float = 0.0,
        threat_cue: float = 0.0,
        pain: float = 0.0,
        reward_expectation: float = 0.0,
    ) -> "AffectState":
        """Advance the affect state by one tick given external drivers.

        Parameters
        ----------
        rpe:
            Reward prediction error (positive -> pleasant/approach).
        threat_cue:
            Instantaneous threat input in [0, 1].
        pain:
            Nociceptive-like input in [0, 1]; raises arousal and threat and
            lowers valence. (A sensory signal, NOT subjective pain.)
        reward_expectation:
            Current expected reward in [0, 1], drives motivation.
        """
        p = self.params
        threat_cue = _clip(threat_cue, 0.0, 1.0)
        pain = _clip(pain, 0.0, 1.0)

        # Valence: decays toward 0, pushed by RPE and pulled down by pain.
        self.valence = _clip(
            p.valence_decay * self.valence + p.rpe_to_valence * rpe - 0.7 * pain,
            -1.0, 1.0,
        )

        # Arousal: decays toward 0, raised by |rpe|, threat and pain.
        drive = abs(rpe) + threat_cue + pain
        self.arousal = _clip(
            p.arousal_decay * self.arousal + (1.0 - p.arousal_decay) * drive,
            0.0, 1.0,
        )

        # Threat: slow decay first, then a fast rise toward 1 on a cue (or pain).
        cue = max(threat_cue, pain)
        base = p.threat_decay * self.threat
        self.threat = _clip(base + p.threat_rise * (1.0 - base) * cue, 0.0, 1.0)

        # Frustration: accumulates from negative RPE (omitted/blocked reward).
        neg = max(0.0, -rpe)
        self.frustration = _clip(
            p.frustration_decay * self.frustration + p.frustration_gain * neg,
            0.0, 1.0,
        )

        # Motivation: approach drive from expected reward and arousal,
        # suppressed by threat.
        self.motivation = _clip(
            _clip(reward_expectation, 0.0, 1.0) * (0.5 + 0.5 * self.arousal)
            * (1.0 - 0.5 * self.threat),
            0.0, 1.0,
        )
        return self

    def as_dict(self) -> dict:
        d = asdict(self)
        d.pop("params", None)
        return d
