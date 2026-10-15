# Findings: Experiment R — a per-state critic removes most of the side effect

**Status:** completed 2026-10-16. 24 runs: 3 conditions × 8 seeds (1200–1207,
never run before) × 8000 ticks. Viscous, no extinctions. Pre-registered at
commit `36743d9`, spec unchanged, no deviations. Report:
[`results/R_state_critic/`](../../results/R_state_critic/REPORT.md).

**Intervention.**
- The `scalar` condition is the learning rule used so far: one running
  reward expectation (TD(0)) per agent.
- `critic: "state"` keeps a separate expectation for each binarised sensor
  state (sensors thresholded at 0.2). The RPE that gates plasticity is then
  "better or worse than usual *in this situation*", the correction that
  Frémaux, Sprekeler & Gerstner (2010) derive for reward-modulated STDP.
- `nolearn` uses fixed, evolved weights.

| Hypothesis | Test (a − b) | Result |
|---|---|---|
| H27a: state critic lowers attacks | scalar − state = +0.074 [0.037, 0.114] | **supported** |
| H27b: … lowers signalling | +0.0089 [0.0038, 0.0131] | **supported** |
| H27c: … lowers sharing (neighbour in reach) | +0.0048 [0.0029, 0.0067] | **supported** |
| H27d: … reduces social-minus-locomotion drift | +0.073 [0.060, 0.086] | **supported** |
| H27e: … improves foraging | state − scalar = +0.0079 [0.0051, 0.0107] | **supported** |

| condition | locomotion drift | attack | share \| neighbour | signal | food per agent-tick |
|---|---|---|---|---|---|
| scalar | −0.033 | 0.115 | 0.0150 | 0.023 | 0.035 |
| state | **+0.045** | 0.040 | 0.0102 | 0.014 | 0.042 |
| nolearn | 0 | 0.017 | 0.0078 | 0.0076 | 0.050 |

## Interpretation

- **The prediction from the literature holds here.** With a per-state
  critic, locomotion weights no longer fall (they grow by 4.5%). The
  learning-induced rise in social actions shrinks:
  - attacks by 76%;
  - signalling by 58%;
  - sharing by 66%.
- This is the fifth intervention to point the same way (I, J, K, P, R). It is
  the first one that is a usable learning rule rather than a diagnostic.
- **Learning still does not pay.** The state critic recovers about half of
  the foraging cost (scalar −0.015, state −0.007 [−0.010, −0.004] food per
  agent-tick vs no learning), but learners still eat less than agents with
  fixed, evolved wiring. Attacks also stay above no-learning (+0.024
  [0.012, 0.035]).

## Also observed (not pre-registered)

- **Innate foraging** (an evolved trait) was 9.7 with a state critic, 6.6
  with a scalar critic and 11.5 without learning. The hiding effect from E
  looks weaker with the better rule. That is a single comparison, untested.
- The **early birth rate** was much higher with the scalar critic (0.0036 vs
  0.0014 state, 0.0010 nolearn), and so was the number of generations (9.6 vs
  7.0 vs 6.9). One possible reason is that attacks transfer energy and speed
  up turnover. Untested.

## Limits

- 8 seeds, 8000 ticks, viscous populations only.
- The state key uses up to 2048 binarised states. Rarely visited states keep
  near-zero expectations, so in those states the rule acts like the scalar
  critic.
- The per-state critic also feeds affect (the RPE and the reward expectation
  in `learn_and_affect`). Some of the effect could come through affect
  rather than plasticity.

## Next step

Agenda item 15: does any rule make lifetime learning pay in evolving
populations? The state critic is the baseline to beat.
