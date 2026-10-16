# Findings: Experiment Q6 — parental culling does not explain why being born beside the parent protects populations

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(2200–2211, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `f51551b`, spec unchanged, no deviations. No pilot. Run time 66 min.
Report: [`results/Q6_parental_culling/`](../../results/Q6_parental_culling/REPORT.md).

**Intervention.** `no_filial_attack=True`: if the nearest target of an attack
is the attacker's own offspring, the attack has no effect. The attacker still
pays the cost. Newborns are placed beside the parent.

| Hypothesis | Test (parent_noattack − parent) | Result |
|---|---|---|
| H39a: without culling, populations die out sooner | +395 [−648, 1590] ticks | not supported |
| H39b: without culling, populations go extinct more often | −0.08 [−0.33, 0.17] | not supported |
| H39c: without culling, population size swings more (CV) | −0.031 [−0.067, 0.003] | not supported (if anything, less) |
| H39d: manipulation check, kills of own offspring < 5% | 0% of kills | **supported** |

**By the pre-registered rule (neither H39a nor H39b supported), parental
culling is not the mechanism.** The parent protects the population some
other way.

| condition | extinct | mean survival | early birth rate | kills of own offspring | kills of young | starvation share | final population |
|---|---|---|---|---|---|---|---|
| beside parent | 3/12 | 17188 | 0.0037 | 40% | 67% | 31% | 24.4 |
| beside parent, no filial attack | **2/12** | 17583 | 0.0022 | 0% | 38% | 43% | 30.0 |
| beside a stranger | 10/12 | 13067 | 0.0031 | 4% | 54% | 38% | 6.0 |

## Interpretation

- **The protection survives without filial killing.** The extinction counts
  were 2/12 without filial attacks and 3/12 with them. In the five studies
  that ran both (Q, Q2, Q3, Q5, Q6), stranger placement went extinct in 56/60
  runs and parent placement in 18/60.
- **Birth rate does not explain persistence either.** Without filial attacks
  the early birth rate fell by 40% (0.0022 vs 0.0037), but populations
  survived as well as before. In Q3 and Q4 lower birth rates also did not
  predict extinction.
- **A candidate that fits the data so far: the newborn absorbs aggression.**
  An attack hits the nearest agent. When newborns sit beside their parent,
  the nearest target of a parent's attack is often its own young, which is
  cheap to lose and soon replaced. When newborns are placed elsewhere,
  attacks more often land on established, foraging adults. Kills of young
  agents were 67% of kills beside the parent here (66% in Q4), against 54%
  beside strangers. With `no_filial_attack`, attacks aimed at offspring do
  nothing at all, so they still hit no adult. One fact does not fit neatly:
  in that condition kills of young fell to 38%, below the stranger condition,
  yet the population was protected. The account is post hoc and untested.

## Next step

Q7 tests the aggression-sink account directly. Keep newborns beside the
parent, but redirect any attack aimed at one's own offspring to the nearest
other agent in reach. If protection disappears, the sink is the mechanism.
