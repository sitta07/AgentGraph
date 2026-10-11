# Findings: Experiment G — is learned sharing a gift-reward reciprocity loop?

**Status:** completed 2026-10-12. 18 runs: 3 conditions × 6 seeds × 8000
ticks. No population went extinct. Pre-registered at commit `591d801`, spec
unchanged, no deviations. Report:
[`results/G_gift_reward_reciprocity/`](../../results/G_gift_reward_reciprocity/REPORT.md).

| Hypothesis | Test (share rate given a neighbour in reach) | Result |
|---|---|---|
| H13c: replication — learning raises sharing | learn_gift − nolearn = **+0.0086 [0.0064, 0.0108]** | supported (third replication) |
| H13: removing the gift reward lowers learned sharing | learn_gift − learn_nogift = +0.0019 [0.0004, 0.0036] | supported |
| H13b: without the gift reward, learning no longer raises sharing | learn_nogift − nolearn = +0.0067 [0.0057, 0.0076] | **difference detected**: the null is rejected |

## Interpretation

- The gift-reward reciprocity loop is real but **explains only ≈22%** of the
  learning effect on sharing (0.0019 of 0.0086).
- Most of the effect remains when the loop is removed, so another mechanism
  dominates.
- **A candidate, not yet tested:**
  - Learning raised attacks ~10× as well (14.6% vs 1.3% of agent-ticks). This
    suggests a *non-specific* effect.
  - The social action populations start with weaker input weights
    (`w_social_scale = 0.85`).
  - Potentiation-only reward-modulated plasticity may pull all of them up
    toward parity with locomotion.

## Reproducibility check

The `learn_gift` and `nolearn` conditions use exactly the same configuration
and seeds as `learn` and `nolearn` in Experiment E. The two separate runs
produced **identical numbers** (for example, innate foraging 5.354 and 9.729).
This confirms determinism across independent invocations.
