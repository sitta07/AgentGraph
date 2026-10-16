# Findings: Experiment Q9 — redirecting attacks within the family both ways does not clearly remove the protection

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(2600–2611, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `c71c5c8`, spec unchanged, no deviations. No pilot. Run time 91 min.
Report: [`results/Q9_family_redirect/`](../../results/Q9_family_redirect/REPORT.md).

**Intervention.** `family_attack_redirect=True`: when the nearest target of
an attack is the attacker's own offspring or own parent, the attack hits the
nearest agent in reach that is neither (or misses). Newborns are placed
beside the parent. This closes the gap left by [Q8](FINDINGS_Q8.md), where
blocked attacks never reached unrelated adults.

| Hypothesis | Test (parent_redirect − parent) | Result |
|---|---|---|
| H45a: with redirection, populations die out sooner | −553 [−2725, 1456] ticks | not supported |
| H45b: with redirection, populations go extinct more often | +0.17 [−0.17, 0.50] | not supported |
| H45c: manipulation check, kills of own offspring < 5% | 0% of kills | **supported** |
| H45d: manipulation check, fewer kills are of kin | −0.33 [−0.39, −0.27] | **supported** |

**By the pre-registered rule (neither H45a nor H45b supported), the broad
sink account is not supported.** The effect points the predicted way,
however, and is larger than in Q6–Q8.

| condition | extinct | mean survival | early birth rate | kills of own offspring | kills of kin | starvation share | attack rate | final population |
|---|---|---|---|---|---|---|---|---|
| beside parent | 4/12 | 16172 | 0.0043 | 43% | 64% | 29% | 0.23 | 24.0 |
| beside parent, family attacks redirected | 6/12 | 15619 | 0.0025 | 0% | 31% | 39% | 0.30 | 16.0 |
| beside a stranger | 11/12 | 12250 | 0.0030 | 4% | 33% | 36% | 0.28 | 1.3 |

Fisher exact (two-sided, not pre-registered): parent vs stranger p = 0.009;
redirect vs stranger p = 0.069; parent vs redirect p = 0.68.

## Interpretation

- **Kills of kin fell to the stranger level** (31% vs 33%). By who gets
  killed, the redirected populations look like stranger populations.
  Extinctions rose from 4/12 to 6/12, still well below 11/12.
- **Q6–Q9 together.** Changing which family attacks land, in four
  different ways, never produced a clear loss of protection: 2/12, 3/12,
  5/12 and 6/12 extinct, against 3/12, 4/12, 4/12 and 4/12 for the paired
  parent conditions. Summed over the four studies, that is 16/48 with the
  intervention vs 15/48 without. Q9's shift is the only one in the predicted
  direction of any size, and it is not significant. A partial role for the
  sink cannot be excluded at this sample size.
- Pooled over the eight studies with both placements, stranger placement
  went extinct in 88/96 runs and parent placement in 30/96.
- Redirection lowered the birth rate (0.0025 vs 0.0043) and raised the
  attack rate (0.30 vs 0.23), the latter because more attacks now land.

## Next step

The leading untested candidate is what the newborn senses. Beside the
parent, its "other agent" sensors respond to its parent rather than to a
stranger. A direct test: blind newborns to their
parent (the parent is invisible to the child's agent sensors) with placement
beside the parent.
