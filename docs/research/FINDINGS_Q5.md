# Findings: Experiment Q5 — the protection comes from starting beside the parent, not beside relatives

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds
(2100–2111, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `11f807b`, spec unchanged, no deviations. No pilot. Run time 53 min.
Report: [`results/Q5_parent_vs_relative/`](../../results/Q5_parent_vs_relative/REPORT.md).

**Intervention.** `born_near_relative=True` places each newborn beside a
random living relative of its parent (recorded relatedness > 0), excluding
the parent itself. If there is none, the newborn goes beside the parent.
That happened in 1.6% of births.

| Hypothesis | Test (a − b) | Result |
|---|---|---|
| H37a: kin neighbourhood, relative survives longer than stranger | +1425 [−809, 3713] ticks | not supported |
| H37b: kin neighbourhood, relative goes extinct less often than stranger | −0.17 [−0.42, 0.00] | not supported |
| H37c: parent-specific, parent survives longer than relative | +3848 [715, 6844] ticks | **supported** |
| H37d: parent-specific, parent goes extinct less often than relative | −0.67 [−0.92, −0.42] | **supported** |
| H37e: manipulation check, fallback to the parent in < 50% of births | 1.6% | **supported** |

**By the pre-registered rule (H37c and H37d supported, H37a and H37b not),
the protection is parent-specific.**

| condition | extinct | mean survival | early birth rate | kills of own offspring | kills of kin | starvation share | final population |
|---|---|---|---|---|---|---|---|
| beside parent | **2/12** | 16710 | 0.0039 | 42% | 62% | 30% | 30.0 |
| beside another relative | 10/12 | 12862 | 0.0031 | 5% | 43% | 37% | 6.0 |
| beside a stranger | 12/12 | 11437 | 0.0029 | 3% | 30% | 37% | 0.0 |

Fisher exact (two-sided, not pre-registered): parent vs relative p = 0.003;
relative vs stranger p = 0.48; parent vs stranger p = 0.0001.

## Interpretation

- **Being placed beside a sibling or cousin is nearly as bad as being placed
  beside a stranger.** Only placement beside the parent protects the
  population. Across Q–Q5, newborns placed beside a stranger went extinct in
  46/48 runs.
- **Kin-selection accounts that work through relatedness in general are
  therefore unlikely here.** Relatives other than the parent are related to
  the newborn by 0.25–0.5, yet they give no measurable protection.
- **Placement beside the parent is also where parents kill their own
  offspring** (42% of kills, against 3–5% elsewhere). Q3 showed that the
  energy the parent gains from those kills is not what protects the
  population. It did not test whether the killing itself matters. When
  parents cull their newborns, they may hold population growth below the level
  that leads to a crash. That is untested.
- Births were also faster beside the parent (0.0039 vs 0.0029–0.0031 per
  agent-tick). Faster births and frequent filial killing together suggest
  high turnover within each family.

## Next step

Q6: make attacks on one's own offspring impossible (they have no effect at
all), with placement beside the parent. If the protection disappears,
parental culling is the mechanism. If it stays, the parent protects its
offspring some other way, for example as a nearby neighbour that does not
compete the way unrelated adults do.
