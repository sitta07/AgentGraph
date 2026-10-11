"""Reward prediction and the dopamine-inspired reward prediction error (RPE).

Scientific basis
----------------
The reward prediction error is the central quantity of temporal-difference (TD)
reinforcement learning (Sutton 1988; Sutton & Barto 2018) and is the dominant
computational account of phasic dopamine signalling (Schultz, Dayan & Montague
1997, *Science* 275:1593). For a transition with reward ``r`` from a state with
value estimate ``V(s)`` to a next state with value ``V(s')``:

    delta = r + gamma * V(s') - V(s)          # TD error / RPE
    V(s) <- V(s) + alpha * delta              # value update

Positive RPE ("better than expected") reinforces; negative RPE ("worse than
expected") punishes. We expose ``delta`` as a scalar modulator that can gate
reward-modulated STDP in the spiking network (a three-factor learning rule).

Simplification
--------------
This is the standard engineering TD(0) rule. The mapping "RPE == dopamine" is a
well-supported but still debated hypothesis, not an identity; we treat ``delta``
purely as a learning signal.
"""

from __future__ import annotations


class RewardPredictor:
    """Tabular / scalar TD(0) value estimator producing reward prediction error."""

    def __init__(self, alpha: float = 0.2, gamma: float = 0.0, v_init: float = 0.0) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        if not 0.0 <= gamma < 1.0:
            raise ValueError("gamma must be in [0, 1)")
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self._values: dict[object, float] = {}
        self.v_init = float(v_init)

    def value(self, state: object = "_") -> float:
        """Current value estimate for a (hashable) state key."""
        return self._values.get(state, self.v_init)

    def prediction_error(self, reward: float, state: object = "_",
                         next_state: object | None = None) -> float:
        """Compute the RPE for this transition without updating the estimate."""
        v_next = 0.0 if next_state is None else self.value(next_state)
        return float(reward) + self.gamma * v_next - self.value(state)

    def update(self, reward: float, state: object = "_",
               next_state: object | None = None) -> float:
        """Compute the RPE, update the value estimate, and return the RPE."""
        delta = self.prediction_error(reward, state, next_state)
        self._values[state] = self.value(state) + self.alpha * delta
        return delta

    def reset(self) -> None:
        self._values.clear()
