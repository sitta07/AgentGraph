# Findings: Experiment T — no learning rule tested makes lifetime learning pay

**Status:** completed 2026-10-16. 40 runs: 5 conditions × 8 seeds
(1700–1707, never run before) × 8000 ticks. Viscous, no extinctions.
Pre-registered at commit `3ce7a2c`, spec unchanged, no deviations. No pilot
was run. Report:
[`results/T_learning_rules/`](../../results/T_learning_rules/REPORT.md).

| Hypothesis (food per agent-tick) | Test (a − b) | Result |
|---|---|---|
| H32a: replication of R, state > scalar | +0.0072 [0.0043, 0.0099] | **supported** |
| H32b: chosen-only credit improves on state | +0.0014 [−0.0017, 0.0043] | not supported |
| H32c: low learning rate improves on state | +0.0035 [−0.0003, 0.0071] | not supported |
| H32d: learning still costs (state + chosen-only) | −0.0057 [−0.0085, −0.0027] vs no learning | **supported** |
| H32e: learning still costs (state + low rate) | −0.0036 [−0.0073, −0.0010] vs no learning | **supported** |

| condition | food | vs no learning | attack | locomotion drift |
|---|---|---|---|---|
| scalar (current rule) | 0.0349 | −29% | 0.113 | −0.034 |
| state | 0.0421 | −14% | 0.042 | +0.054 |
| state + chosen-only | 0.0435 | −12% | 0.034 | +0.047 |
| state, lr 0.2 | 0.0456 | −7% | 0.024 | +0.013 |
| no learning | 0.0492 | — | 0.015 | 0 |

## Interpretation

- **R replicates.** The per-state critic again halved the foraging cost of
  learning (−29% → −14%) and cut attacks by more than half.
- **Neither further change helped significantly on its own.** The ordering
  is still informative. Foraging rises steadily as learning is made weaker
  or more targeted. The best rule tested, a quarter of the learning rate,
  still eats 7% less than fixed wiring.
- **In this world, any amount of the current lifetime learning lowers
  foraging.** So far, less learning is always better. That fits the hiding
  effect (E): evolved wiring is already tuned, and lifetime plasticity mostly
  adds noise or bias.
- That is a claim about this rule family (reward-modulated STDP with an
  eligibility trace) in this world. Learning that helps would probably need
  something to learn that evolution cannot fix in advance. A world that
  changes within a lifetime is one example. N and N3 tried this and both
  failed their manipulation checks.

## A non-replication (R's post-hoc observation)

In R, innate foraging looked much higher with the per-state critic than with
the scalar critic (9.7 vs 6.6). Here the difference is small: 8.0 vs 7.5,
with no learning at 9.8. The R observation was not pre-registered and should
be treated as chance. [R](FINDINGS_R.md) and the synthesis page have been
updated.

## Next step

Learning can only pay where there is something to learn within a lifetime.
Build an environmental change that measurably hurts fixed-wiring agents,
check it in a pilot first, and then compare learning rules there (agenda
item 16).
