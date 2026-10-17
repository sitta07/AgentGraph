# Findings: Experiment AD — hiding the parent from its offspring's sensors does not remove the protection

**Status:** completed 2026-10-17. 48 runs: 4 conditions × 12 seeds
(2700–2711, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `644a2bf`, spec unchanged, no deviations. No pilot. Run time 42 min
on the fused network step ([#45](https://github.com/sitta07/NeuralMind/pull/45),
bit-identical results).
Report: [`results/AD_blind_to_parent/`](../../results/AD_blind_to_parent/REPORT.md).

**Intervention.** Sensing only; attacks, shares and placement are unchanged.
`blind_to_parent=True`: an agent's three "other agent" sensors never respond
to its own parent. `blind_to_family=True`: in addition, a parent's sensors
never respond to its own offspring. Newborns are placed beside the parent.

| Hypothesis | Test (vs parent) | Result |
|---|---|---|
| H50a: offspring blind to parent, populations die out sooner | +910 [−1191, 3083] ticks | not supported |
| H50b: offspring blind to parent, more extinctions | −0.08 [−0.50, 0.33] | not supported |
| H50c: blind to each other, populations die out sooner | −79 [−2401, 2423] ticks | not supported |
| H50d: blind to each other, more extinctions | 0.00 [−0.50, 0.42] | not supported |

**By the pre-registered rule (none supported), what the newborn senses does
not explain the protection.**

| condition | extinct | mean survival | early birth rate | kills of kin | kills of own offspring | aggression gene |
|---|---|---|---|---|---|---|
| beside parent | 6/12 | 15772 | 0.0035 | 64% | 43% | 1.26 |
| beside parent, child blind to parent | 5/12 | 16682 | 0.0037 | 66% | 44% | 1.46 |
| beside parent, blind to each other | 6/12 | 15694 | 0.0037 | 60% | 42% | 1.53 |
| beside a stranger | 11/12 | 10302 | 0.0036 | 32% | 4% | 0.63 |

Fisher exact (two-sided, not pre-registered) vs stranger: parent p = 0.069,
child blind p = 0.027, both blind p = 0.069.

## Interpretation

- **Sensing is ruled out at this sample size.** With the parent invisible,
  extinctions were 5/12 and 6/12, against 6/12 beside a visible parent.
- **The parent condition went extinct more often than usual** (6/12; the
  previous eight studies averaged 30/96, about 3.8/12). The stranger
  condition matched its usual rate (11/12).
- **Pooled over nine studies,** stranger placement went extinct in 99/108
  runs and parent placement in 36/108.
- **What has now been ruled out, beside the parent:**
  - parental culling (Q6)
  - the aggression sink, one way (Q7) and both ways (Q9)
  - sharing between parent and offspring (Q8)
  - the newborn sensing its parent, and the parent sensing it (AD)
  - local density alone (Q, Q2)
  - being beside any relative (Q5)

## Next step

The parent has just reached the reproduction threshold, so it is likely to
stand where food has recently been easy to find. A stranger is drawn at
random, wherever it stands. A candidate: newborns beside the parent start in
a better-than-average spot. Test it by placing newborns beside the stranger
with the most energy, and measure crowding and food at each birth site.
