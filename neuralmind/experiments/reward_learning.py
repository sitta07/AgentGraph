"""Experiment 1: reward learning via reward-modulated STDP.

Question
--------
Does a reward prediction error, used as the third factor in a three-factor
STDP rule, shift a spiking agent's action selection toward a rewarded action?

Design
------
A context population projects, via two *plastic* connections, to two competing
action populations (action 0 and action 1). The two action populations inhibit
each other (lateral inhibition / soft winner-take-all), so that on any trial one
population tends to win and suppress the other. On each trial:

1. The context neurons are driven with current plus per-trial noise.
2. Both action populations integrate their synaptic input and compete through
   mutual inhibition; STDP changes are accumulated into eligibility traces.
   Because the winner fires and the loser is suppressed, eligibility is
   concentrated on the *chosen* pathway (this solves credit assignment).
3. The chosen action is the population that fired more spikes.
4. A reward (1 if the chosen action is the rewarded one, else 0) drives a
   TD(0) reward prediction error (:class:`RewardPredictor`).
5. ``net.apply_reward(lr * rpe)`` converts eligibility into a weight change:
   co-active (chosen) synapses are strengthened on positive RPE.

Expected behaviour
------------------
The fraction of trials choosing the rewarded action should rise well above the
chance baseline (0.5) and above a learning-rate-zero control. This is a
qualitative, well-established reinforcement-learning prediction, so the result
is treated as *validated* against that qualitative expectation.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from neuralmind.affect.reward import RewardPredictor
from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFParams, LIFPopulation
from neuralmind.core.plasticity import STDPConfig
from neuralmind.experiments.base import ExperimentResult


@dataclass
class RewardLearningConfig:
    n_ctx: int = 12
    n_action: int = 12
    rewarded_action: int = 0
    n_trials: int = 120
    trial_ms: float = 60.0
    dt: float = 1.0
    ctx_current: float = 6.0
    ctx_noise: float = 2.0       # std of per-step context noise current (shared via ctx)
    action_noise: float = 3.0    # std of independent per-step noise into each action pop
    learning_rate: float = 0.6   # scales rpe -> weight change
    w_init: float = 0.5          # initial (identical) mean synaptic weight
    w_max: float = 3.0
    w_inhib: float = 1.5         # lateral inhibition between action populations
    alpha: float = 0.2           # TD value learning rate
    seed: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


class RewardLearningExperiment:
    def __init__(self, config: RewardLearningConfig | None = None) -> None:
        self.cfg = config or RewardLearningConfig()
        if self.cfg.rewarded_action not in (0, 1):
            raise ValueError("rewarded_action must be 0 or 1")

    def _build(self, rng: np.random.Generator) -> SpikingNetwork:
        c = self.cfg
        net = SpikingNetwork(dt=c.dt)
        net.add_population("ctx", LIFPopulation(c.n_ctx, dt=c.dt))
        stdp = STDPConfig(w_max=c.w_max, tau_eligibility=200.0)
        # Identical initial weights for both pathways -> symmetric baseline.
        w0 = np.clip(rng.normal(c.w_init, c.w_init * 0.2, size=(c.n_action, c.n_ctx)),
                     0.0, c.w_max)
        for k in (0, 1):
            net.add_population(f"a{k}", LIFPopulation(c.n_action, dt=c.dt))
            net.connect(Connection("ctx", f"a{k}", weights=w0.copy(), tau_syn=5.0,
                                   plastic=True, stdp_config=stdp))
        # Lateral inhibition (soft winner-take-all): negative current each way.
        inhib = -abs(c.w_inhib) * np.ones((c.n_action, c.n_action))
        net.connect(Connection("a0", "a1", weights=inhib.copy(), tau_syn=10.0))
        net.connect(Connection("a1", "a0", weights=inhib.copy(), tau_syn=10.0))
        return net

    def run(self, learning: bool = True) -> ExperimentResult:
        c = self.cfg
        rng = np.random.default_rng(c.seed)
        net = self._build(rng)
        predictor = RewardPredictor(alpha=c.alpha)

        steps = int(round(c.trial_ms / c.dt))
        choices: list[int] = []
        rewards: list[float] = []
        rpes: list[float] = []
        correct: list[int] = []

        for _ in range(c.n_trials):
            net.reset()  # resets membrane/synapse/traces/eligibility, keeps weights
            counts = np.zeros(2)
            for _ in range(steps):
                ext = {
                    "ctx": c.ctx_current + rng.normal(0.0, c.ctx_noise, size=c.n_ctx),
                    "a0": rng.normal(0.0, c.action_noise, size=c.n_action),
                    "a1": rng.normal(0.0, c.action_noise, size=c.n_action),
                }
                spikes = net.step(external=ext)
                counts[0] += int(spikes["a0"].sum())
                counts[1] += int(spikes["a1"].sum())

            if counts[0] == counts[1]:
                choice = int(rng.integers(0, 2))
            else:
                choice = int(np.argmax(counts))
            reward = 1.0 if choice == c.rewarded_action else 0.0
            rpe = predictor.update(reward)
            if learning:
                net.apply_reward(c.learning_rate * rpe)

            choices.append(choice)
            rewards.append(reward)
            rpes.append(rpe)
            correct.append(int(choice == c.rewarded_action))

        correct_arr = np.array(correct, dtype=float)
        first = correct_arr[: max(1, c.n_trials // 4)].mean()
        last = correct_arr[-max(1, c.n_trials // 4):].mean()

        result = ExperimentResult(
            name="reward_learning",
            status="validated" if learning else "exploratory",
            config=c.as_dict() | {"learning": learning},
            metrics={
                "final_selection_rate": float(last),
                "initial_selection_rate": float(first),
                "learning_gain": float(last - first),
                "mean_reward": float(np.mean(rewards)),
            },
            series={
                "choice": choices,
                "reward": rewards,
                "rpe": rpes,
                "correct": correct,
            },
            notes=[
                "Reward-modulated STDP (three-factor) with TD(0) RPE as modulator.",
                "Baseline control: run(learning=False) should stay near chance (0.5).",
                "Qualitative RL prediction; not calibrated to any biological dataset.",
            ],
        )
        return result
