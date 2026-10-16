# Findings: Experiment Q — being born next to a stranger does not help; being born next to a parent might

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds (1100–1111,
never run before) × 18000 ticks. Pre-registered at commit `5e4dda8`, spec
unchanged, no deviations. Report:
[`results/Q_kin_vs_density/`](../../results/Q_kin_vs_density/REPORT.md).

**Design.** All three conditions learn.
- `mixed`: newborns are placed at random.
- `viscous`: newborns are placed beside their parent.
- `stranger`: newborns are placed beside a random living agent with
  relatedness 0 to the parent (another founder lineage). If none exists,
  they are placed at random.

The interpretation rule was fixed in advance. If only density matters, H26a
and H26b are supported and H26c and H26d are not. If only kinship matters, it
is the reverse.

| Hypothesis | Test (a − b) | Result |
|---|---|---|
| H26a: density helps survival (stranger > mixed) | −936 [−4148, 2194] ticks | not supported |
| H26b: density raises early birth rate (stranger > mixed) | +0.0004 [−0.0002, 0.0012] | not supported |
| H26c: kinship helps survival (viscous > stranger) | +2902 [−230, 5941] ticks | not supported (CI just crosses 0) |
| H26d: kinship raises early birth rate (viscous > stranger) | +0.0004 [−0.0006, 0.0012] | not supported |
| H14b4: viscous survives longer than mixed (4th test) | +1965 [−337, 4142] ticks | not supported |

**By the pre-registered rule, the result is inconclusive.** Neither pattern
appeared. No hypothesis is supported.

## Extinction counts (not pre-registered)

| condition | extinct by tick 18000 | median survival |
|---|---|---|
| mixed | 8/12 | 15133 |
| stranger | **11/12** | 12465 |
| viscous | **3/12** | 18000 |

- Fisher exact (two-sided): viscous vs stranger p = 0.003; viscous vs mixed
  p = 0.10; stranger vs mixed p = 0.32.
- Placing a newborn beside a non-relative did not protect the population. If
  anything it did worse than random placement, although that difference is
  not significant. Placing it beside its parent protected the population
  much better than placing it beside a stranger.
- **This points toward kinship (or something specific to the parent) rather
  than local density.** This is a post-hoc reading of extinction counts, not
  of the pre-registered survival-time test, so treat it as a lead.
- Possible mechanisms, all untested:
  - non-relatives attack newborns (in L, killings were 58–67% of deaths);
  - kin cluster, so a newborn among kin meets fewer unrelated attackers;
  - a newborn next to a stranger competes with that stranger for the same
    nearby food.
- The early-birth-rate test is noisy. Two `stranger` runs that collapsed
  early (survival 4402 and 10971 ticks) have the highest early birth rates
  (0.0058, 0.0052). Those rates come from very small populations.

## Fourth replication of the viscosity effect

Viscous vs well-mixed survival has now been compared in F2, L and Q. Each
time, viscous populations survived longer on average and fewer went extinct
(F2 7/16 vs 13/16, L 5/16 vs 11/16, Q 3/12 vs 8/12). Here the bootstrap CI
on survival time crosses zero, so H14b4 is not supported on its own.

## Limits

- Final-quarter behaviour metrics for `stranger` come from the one surviving
  run, so the conditions table cannot compare behaviour.
- "Stranger" means relatedness 0 in the registry, which means a different
  founder lineage. Distant cousins within a lineage count as relatives.

## Next step

Log who kills whom (kin or non-kin, newborn or adult) to test the
newborn-attack mechanism directly.
