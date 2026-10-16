# Findings: Experiment P — negative reward errors drive the side effect, and learning hurts foraging

**Status:** completed 2026-10-16. 24 runs: 3 conditions × 8 seeds (1000–1007,
never run before) × 8000 ticks. No population went extinct. Pre-registered
at commit `8a64dca`, spec unchanged, no deviations. Report:
[`results/P_positive_rpe_only/`](../../results/P_positive_rpe_only/REPORT.md).

**Intervention.** `pos_only` skips every weight update whose reward
prediction error (RPE) is negative.

| Hypothesis | Test | Result |
|---|---|---|
| H25a: ignoring negative RPEs lowers attacks | learn_all − pos_only = +0.145 [0.101, 0.206] | **supported** |
| H25b: … lowers signalling | +0.025 [0.018, 0.033] | **supported** |
| H25c: … lowers sharing (neighbour in reach) | +0.013 [0.011, 0.015] | **supported** |
| H25d: with positive RPEs only, locomotion grows more than social inputs | drift difference −0.71 [−0.75, −0.67] | **supported** |
| H25e: with positive RPEs only, attacks are not above no-learning | −0.007 [−0.015, 0.003] | no difference detected |

| condition | locomotion drift | attack | share \| neighbour | signal | food per agent-tick |
|---|---|---|---|---|---|
| learn_all | −0.024 | 0.153 | 0.0156 | 0.027 | 0.035 |
| pos_only | **+0.73** | 0.008 | 0.0024 | 0.0024 | 0.045 |
| nolearn | 0 | 0.015 | 0.0079 | 0.0079 | **0.051** |

## Interpretation

- **The candidate mechanism from the K probe is confirmed.** Remove the
  negative RPEs and the drift reverses: locomotion weights grow by 73%. Social
  actions then fall to the no-learning level or below. Sharing and
  signalling drop to about a third of the no-learning rate.
- Across I, J, K and P, four separate interventions point to the same
  conclusion. **In this model, how often agents act socially is set by the
  balance of total drive between action populations.** The learning rule
  shifts that balance as a side effect. Social behaviour is not being
  learned from its consequences.

## Learning makes foraging worse (not pre-registered, large)

| (food per agent-tick, final quarter) | vs no learning |
|---|---|
| learn_all | −0.016 [−0.019, −0.013] (−31%) |
| pos_only | −0.006 [−0.010, −0.002] (−11%) |

- With the current rule, agents that learn during their lifetime **eat about
  a third less** than agents with fixed, evolved wiring. Part of this is
  because they spend ticks attacking (15% of ticks). Even with positive RPEs
  only, they still eat less than without learning.
- This fits E's hiding effect: the lifetime learning in this model does not
  pay for itself in a social, evolving world.
- It is also a warning for earlier studies. The reward-modulated learner
  "beats a no-learning baseline" in single-agent tests
  (`test_learning_beats_baseline_on_heldout`), but that does not carry over
  to evolved populations.

## Limits

- Ignoring negative RPEs is a diagnostic, not a proposed learning rule.
  Weights only grow, up to `w_max`.
- `food_rate` was added for Experiment N, so earlier studies cannot be
  re-checked for the foraging cost.
