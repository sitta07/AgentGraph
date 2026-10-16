# Findings: Experiment W — with slow, fresh and balanced decisions, lifetime learning finds sensory foraging and pays about 5.7×

**Status:** completed 2026-10-16. 60 runs: 5 conditions × 12 training seeds
(600–611) × 40 training episodes, each agent tested on 16 held-out worlds
(9100–9115). Training seeds and test worlds had never been run. Single
agents, 500-tick episodes. Pre-registered at commit `2bfa1cf`, spec
unchanged, no deviations. A 12-seed pilot on other seeds preceded
registration (see [`FINDINGS_V.md`](FINDINGS_V.md), follow-up). Run time 14 min.
Report: [`results/W_decision_dynamics/`](../../results/W_decision_dynamics/REPORT.md).

**The three fixes.**
1. `substeps=32`: one decision lasts 32 ms of simulated time instead of 8 ms,
   longer than the 20 ms membrane time constant.
2. `reset_each_decision=True`: membrane and synaptic state are cleared before
   every decision, so the previous winner does not carry over.
3. `normalize=True`: each action neuron's total input weight is held at its
   starting value, which stops one pathway from running away.

| Hypothesis | Test | Result |
|---|---|---|
| H38a: with all three fixes, trained agents eat more than with the default dynamics | +15.9 [14.1, 17.2] food per episode | **supported** |
| H38b: with all three fixes, learning pays (trained − untrained) | +15.4 [14.3, 16.5] | **supported** |
| H38c: with all three fixes, trained agents use their senses (real − scrambled) | +15.9 [14.8, 17.0] | **supported** |
| H38d: clearing state is necessary (full − no_reset) | +16.7 [15.2, 18.1] | **supported** |
| H38e: the 32 ms window is necessary (full − no_window) | +15.1 [13.7, 16.3] | **supported** |
| H38f: normalisation is necessary (full − no_norm) | +15.9 [14.4, 17.3] | **supported** |
| H38g: replication, default learning raises foraging | −0.69 [−1.65, 0.32] | not supported |

| condition | trained | trained, scrambled senses | untrained | collapsed learners (< 1 food) | per-seed trained range |
|---|---|---|---|---|---|
| default | 2.81 | 2.03 | 3.50 | 2/12 | 0.4–6.5 |
| **full** | **18.67** | 2.75 | 3.25 | **0/12** | **15.1–21.9** |
| no_reset | 1.95 | 2.03 | 1.44 | 5/12 | 0.1–5.4 |
| no_window | 3.60 | 2.99 | 2.56 | 0/12 | 2.8–4.6 |
| no_norm | 2.78 | 1.28 | 3.25 | 6/12 | 0.1–8.6 |

**By the pre-registered rule (H38a–c supported), the fixes make lifetime
learning work, and each of the three is necessary (H38d–f).**

## Interpretation

- **This is the first condition in the project where lifetime learning
  clearly pays.** Every one of the 12 trained agents ate 15–22 food per test
  episode in worlds it had never seen. Untrained agents ate 3.25, and the same
  trained agents with scrambled senses ate 2.75. The learned behaviour is
  sensory-guided foraging.
- **The three fixes act together.** Each alone, or any two, leaves foraging
  at 2–4 food per episode. Without normalisation, half the learners
  collapsed, one pathway saturated, and the agent turned in circles (the
  instability Skorheim, Lonjers & Bazhenov 2014 report for rewarded STDP).
  Without clearing state, choice locks in. Without the longer window, sensory
  input barely reaches the action populations before the decision is made.
- **The earlier "+40% from training" single-agent result did not
  replicate.** With the default dynamics, trained agents ate 2.81 against 3.50
  untrained on fresh seeds (H38g). The README's earlier figure (4.85 vs 3.45 on
  60 worlds) came from one agent and is superseded.
- Trained full agents chose "forward" in only 7% of ticks. They move mostly
  by turning, which also moves the body at half speed. How they steer was not
  analysed.

## Limits

- Single agents in a non-social world with 8 food items. In an exploratory
  pilot with evolving social populations (2 seeds × 3000 ticks), the same
  fixes plus learning drove attacks to 26–36% of actions and both
  populations went extinct within 1000–3000 ticks. With uniform choice, the
  attack population wins about one decision in six from the start, and
  learning reinforces theft. The default dynamics hide this, because lock-in
  in movement suppresses attacks. Making the fixes work in social worlds is
  open.
- A decision of 32 substeps costs about 4× the compute of 8.

## Next step

Find a social configuration in which the fixed dynamics do not cause mass
killing (for example weaker innate social weights). Then test whether
learning pays, and whether sensing evolves, in evolving populations.
