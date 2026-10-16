# Findings: Experiment Q8 — blocking parent–offspring attacks and sharing does not remove the protection

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(2500–2511, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `1e4eeca`, spec unchanged, no deviations. No pilot. Run time 90 min.
Report: [`results/Q8_family_isolation/`](../../results/Q8_family_isolation/REPORT.md).

**Intervention.** `no_family_interaction=True`: attacks and shares between a
parent and its own offspring, in either direction, have no effect. An
attacker still pays the attack cost. Newborns are placed beside the parent.

| Hypothesis | Test (parent_isolated − parent) | Result |
|---|---|---|
| H44a: with interaction blocked, populations die out sooner | +1056 [−989, 3345] ticks | not supported |
| H44b: with interaction blocked, populations go extinct more often | +0.08 [−0.33, 0.50] | not supported |
| H44c: manipulation check, kills of own offspring < 5% | 0% of kills | **supported** |
| H44d: manipulation check, fewer gifts go to kin | −0.27 [−0.37, −0.18] | **supported** |

**By the pre-registered rule (neither H44a nor H44b supported), the
protection does not work through attacks or sharing between parent and
offspring.**

| condition | extinct | mean survival | early birth rate | kills of own offspring | kills of young | gifts to kin | starvation share | final population |
|---|---|---|---|---|---|---|---|---|
| beside parent | 4/12 | 15845 | 0.0034 | 41% | 67% | 38% | 32% | 21.2 |
| beside parent, family interaction blocked | 5/12 | 16901 | 0.0025 | 0% | 42% | 11% | 43% | 21.0 |
| beside a stranger | 10/12 | 11912 | 0.0032 | 3% | 55% | 8% | 37% | 6.0 |

Fisher exact (two-sided, not pre-registered): parent vs stranger p = 0.036;
blocked vs stranger p = 0.089; parent vs blocked p = 1.0.

## Interpretation

- **Parent–offspring sharing is not the mechanism.** Gifts to kin fell from
  38% to 11%, close to the stranger level (8%), and the protection stayed.
- **Pooled over the seven studies with both placements** (Q, Q2, Q3, Q5, Q6,
  Q7, Q8), stranger placement went extinct in 77/84 runs and parent
  placement in 26/84.
- **A gap in this design.** A blocked attack does nothing, so an attack
  between parent and offspring still does not reach an unrelated adult.
  Q8 therefore does not rule out a broad version of the aggression sink,
  where attacks between close family members are wasted instead of hitting
  others. Q7 redirected only the parent's attacks. The offspring's attacks
  on its parent were never redirected.
- Blocking lowered the birth rate by about 26%, as in Q6 and Q7, and the
  populations again survived at least as well.

## Next step

Redirect attacks in both directions (parent on offspring and offspring on
parent) to the nearest unrelated agent in reach. If the protection
disappears, the broad sink account holds. If it stays, the remaining
candidate is what the newborn senses: beside its parent, its "other agent"
sensors respond to the parent instead of to a stranger.
