# Findings: Experiment J — learning raises social actions by weakening locomotion

**Status:** completed 2026-10-15. 24 runs: 3 conditions × 8 seeds (300–307,
never run before) × 8000 ticks. No population went extinct. Pre-registered at
commit `a2e1b47`, spec unchanged, no deviations. Report:
[`results/J_locomotion_weakening/`](../../results/J_locomotion_weakening/REPORT.md).

**Question.** Experiment I found that every input weight falls over a
lifetime and locomotion weights fall the most. Action choice is a spike-count
competition between action populations. So does learning raise attacking,
sharing and signalling only because locomotion gets weaker?

**Intervention.** `frozen_loco` keeps the input weights of left, forward and
right at their innate values. Social inputs keep learning.

| Hypothesis | Test | Result |
|---|---|---|
| H19a: freezing locomotion lowers attacks | learn_all − frozen_loco = +0.099 [0.072, 0.130] | **supported** |
| H19b: freezing locomotion lowers signalling | +0.018 [0.012, 0.025] | **supported** |
| H19c: freezing locomotion lowers sharing (neighbour in reach) | +0.0067 [0.0060, 0.0075] | **supported** |
| H19d: with locomotion frozen, learning no longer raises attacks | frozen_loco − nolearn = −0.0004 [−0.0033, 0.0026] | no difference detected |
| H19m: manipulation check, social − locomotion drift under learning | +0.034 [0.025, 0.045] | supported (replicates I) |

| condition | attack rate | signal rate | share \| neighbour | innate foraging |
|---|---|---|---|---|
| learn_all | 0.112 | 0.026 | 0.0146 | 5.0 |
| frozen_loco | 0.013 | 0.008 | 0.0079 | 10.8 |
| nolearn | 0.013 | 0.008 | 0.0074 | 12.3 |

## Interpretation

- **With locomotion frozen, social actions run at the no-learning level.**
  Social inputs were still learning, yet attack, signal and share rates sat
  at their no-learning values. The H19d interval is narrow: ±0.003 around
  zero, against a learning effect of 0.10. That is a "no difference" result,
  which is weaker evidence than a positive one, but the bound is tight.
- **Across C, C2, E, G and I, the "learned" rise in sharing and aggression is
  best explained as a side effect.** Reward-modulated learning lowers the
  locomotion input weights (drift −0.038). That lets the social populations
  win the action competition more often. Social behaviour itself is not being
  learned.
- This also accounts for G (removing the gift reward changed little) and I
  (chosen-only credit changed little for attacks). Neither intervention
  touched locomotion.
- Earlier write-ups called sharing "learned". The behaviour is real: agents
  do share more. But it is not *learned sharing* in the sense of reward
  shaping a social policy.

## Side observation (not pre-registered)

The hiding effect (E, I) mostly disappears when locomotion is frozen. Innate
foraging was 10.8 under frozen_loco against 5.0 under learn_all, and 12.3
without learning. This fits E's account: learning that compensates for poor
inborn foraging wiring shields that wiring from selection.

## Limits

- **Freezing locomotion also removes all lifetime learning of foraging.** The
  result shows that locomotion learning is needed for the social rise. It
  does not separately show that the *weakening* is the cause, rather than
  some other change in foraging behaviour. A cleaner test would keep
  foraging learning but hold the total locomotion input fixed (for example,
  row normalisation on the locomotion inputs only).
- We have not explained *why* locomotion weights fall. A likely candidate is
  negative RPEs after shaped approach rewards, but this is untested.
- One ecology, viscous populations only, 8 seeds.
