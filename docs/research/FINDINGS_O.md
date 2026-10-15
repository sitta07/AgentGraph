# Findings: Experiment O — Q-learners neither win nor lose, but they make lineage fate all-or-nothing

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds (800–811,
never run before) × 6000 ticks. Pre-registered at commit `5eb649e`, spec
unchanged, no deviations. Report:
[`results/O_rl_invasion/`](../../results/O_rl_invasion/REPORT.md).

**Design.**
- Six of the twelve founders, and all their descendants, are driven by
  tabular Q-learners ([`invasion.py`](../../neuralmind/research/invasion.py)).
- In `q_fresh`, every newborn starts with a zero Q-table. In `q_inherit`,
  it copies its parent's table.
- `label` marks the same six lineages but leaves them SNN-driven. It
  measures neutral drift.

| Hypothesis | Test (mean share of population in marked lineages) | Result |
|---|---|---|
| H24a: inherited-table Q-learners out-compete SNNs | q_inherit − label = −0.12 [−0.39, 0.16] | not supported |
| H24b: fresh-table Q-learners lose | q_fresh − label = −0.02 [−0.31, 0.27] | not supported |
| H24c: inheriting the table matters | −0.09 [−0.35, 0.15] | not supported |
| H24d: neutral control holds about half | 0.55 [0.45, 0.66] | no difference from 0.5 detected |

**The pilot misled us.** The predictions came from one unregistered seed
(9999), where inherited-table Q-learners reached 100% and fresh-table ones
fell to 3%. Neither direction held across 12 fresh seeds. A single pilot seed
cannot show a direction. We record this so the lesson stays visible.

## What did differ: how often a lineage type takes over or disappears (not pre-registered)

By tick 6000, either one controller type had taken over the whole
population, or the marked lineages were gone:

| condition | took over | disappeared | still mixed |
|---|---|---|---|
| label (SNN vs SNN) | 2 | 2 | 8 |
| q_fresh | 6 | 6 | 0 |
| q_inherit | 3 | 7 | 2 (1 population extinct) |

- All-or-nothing outcomes: 12/12 for q_fresh against 4/12 for label (Fisher
  p = 0.001), and 10/12 for q_inherit (p = 0.04).
- Which side wins looks like a coin flip. Once one controller type pulls
  ahead, it takes over quickly.
- This is consistent with positive frequency dependence, for example if
  each type does better when surrounded by its own kind. That explanation is
  untested.
- Q-learner populations also attacked more (0.16–0.23 vs 0.09) and ate less
  (0.028–0.032 vs 0.035 food per agent-tick).

## Limits

- The Q-learners are deliberately simple: 2048 binarised states,
  ε = 0.05, no tuning.
- Q-learners see the world at the start of each tick (a small information
  lag; see `invasion.py`).
- 6000 ticks, viscous populations only.
