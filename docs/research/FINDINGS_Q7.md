# Findings: Experiment Q7 — newborns do not protect the population by absorbing attacks

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(2400–2411, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `34a394a`, spec unchanged, no deviations. No pilot. Run time 75 min.
Report: [`results/Q7_aggression_sink/`](../../results/Q7_aggression_sink/REPORT.md).

**Intervention.** `filial_attack_redirect=True`: when the nearest target of
an attack is the attacker's own offspring, the attack hits the nearest other
agent within reach instead (or misses if there is none). Newborns are placed
beside the parent.

| Hypothesis | Test (parent_redirect − parent) | Result |
|---|---|---|
| H41a: with redirection, populations die out sooner | +611 [−1694, 2959] ticks | not supported |
| H41b: with redirection, populations go extinct more often | −0.08 [−0.50, 0.33] | not supported |
| H41c: manipulation check, fewer kills are of young agents | −0.24 [−0.27, −0.21] | **supported** |
| H41d: manipulation check, kills of own offspring < 5% | 0% of kills | **supported** |

**By the pre-registered rule (neither H41a nor H41b supported), the
aggression-sink account is not supported.** The manipulation worked: kills
of young agents fell from 65% to 41%, below the stranger condition (53%).
The protection stayed.

| condition | extinct | mean survival | early birth rate | kills of own offspring | kills of young | starvation share | attack rate | final population |
|---|---|---|---|---|---|---|---|---|
| beside parent | 4/12 | 16320 | 0.0033 | 41% | 65% | 32% | 0.20 | 24.0 |
| beside parent, attacks on offspring redirected | **3/12** | 16931 | 0.0024 | 0% | 41% | 40% | 0.20 | 24.8 |
| beside a stranger | 11/12 | 11929 | 0.0029 | 4% | 53% | 36% | 0.24 | 3.0 |

Fisher exact (two-sided, not pre-registered): redirect vs stranger
p = 0.003; parent vs stranger p = 0.009; parent vs redirect p = 1.0.

## Interpretation

- **Who gets attacked does not explain the protection.** Q6 made attacks
  on one's own offspring ineffective, and Q7 sent them to other adults
  instead. Neither change removed the protection. Across the six studies
  that ran both placements (Q, Q2, Q3, Q5, Q6, Q7), stranger placement went
  extinct in 67/72 runs and parent placement in 22/72.
- **Ruled out so far:** local density (Q, Q2), recycling of the victim's
  energy (Q3), gradual spatial spread (Q4), relatedness in general (Q5),
  parental culling (Q6), and the aggression sink (Q7).
- **What is left (untested):** Q4 found that placing newborns only 0.15
  from the parent already removed most of the protection (8/12 extinct).
  The reach for attacks and sharing is 0.08, so the protection seems to
  need parent and newborn within reach of each other. Food is scattered
  uniformly at random, so a "good food patch" around the parent is unlikely.
  Q6 and Q7 changed only the parent's attacks on its offspring. Other
  interactions within reach were left intact: the newborn's own actions
  (its nearest target is often the parent) and the parent's sharing with it.
  One of these, or their combination, is the remaining candidate.
- Redirection lowered the early birth rate by about 27% (0.0024 vs 0.0033),
  as `no_filial_attack` did in Q6. In both studies the populations survived
  at least as well with fewer births.

## Next step

Block every parent–offspring interaction in both directions (attacks and
sharing have no effect between them), with newborns beside the parent. If
the protection disappears, it works through interaction within reach; then
separate the directions.
