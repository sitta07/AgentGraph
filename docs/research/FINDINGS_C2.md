# Findings: Experiment C2 — crowding, spatial kin cues, and an unexpected extinction pattern

**Status:** completed 2026-10-12. 24 runs: 2×2 conditions × 6 seeds × 18000
ticks, up to ~90 generations. Report:
[`results/evolution_c2/`](../../results/evolution_c2/REPORT.md).

## Pre-registered tests

| Hypothesis | Result | Verdict |
|---|---|---|
| H9 (crowding explains the learning effect on sharing) | The conditional effect, +0.011 [0.003, 0.022], is **100.6%** of the unconditional effect. Encounter rates are nearly equal (0.499 vs 0.488). | **falsified** — learning raises sharing for another reason |
| H10a (share partners are closer than average neighbours) | +0.0005 [−0.0005, 0.0015] | not supported |
| H10b (kin neighbours are closer than non-kin) | +0.0034 [0.0026, 0.0042] | supported |
| H5 re-test (viscosity raises the innate share drive) | −0.023 [−0.061, 0.016] | **not replicated**, so C's nominal H5 was likely a false positive |

The kin bias in sharing **replicated descriptively**:

| Condition | Shares that went to kin | Encounters that were with kin |
|---|---|---|
| viscous + learning | 46% | 35% |
| viscous + no learning | 27% | 18% |

Its mechanism is still open. Distance alone (H10a) does not explain it.

## Unexpected observation (exploratory, not pre-registered)

| Condition | Extinct by tick 18000 |
|---|---|
| viscous + learning | 1/6 |
| viscous + no learning | 1/6 |
| **well-mixed + learning** | **5/6** |
| well-mixed + no learning | 2/6 |

- Overall, viscous populations went extinct in 2/12 runs and well-mixed in
  7/12 (Fisher exact p = 0.089). That is **not significant**.
- In the single surviving well-mixed + learning run, the aggression gene
  reached 3.2. Viscous runs reached ~1.9.
- This resembles Kerr et al. (2006), where local migration promoted restraint
  and avoided a tragedy of the commons.
- Because it was not pre-registered and is underpowered, it is registered as
  **Experiment F** (12 seeds).

## Caveat on all C2 metrics

Final-window metrics come only from populations alive in that window. Where
extinctions differ between conditions, those comparisons carry survivorship
bias. This mostly affects the well-mixed conditions. H9, H10 and H5 compare
conditions with similar extinction counts, except H5 (mixed_nolearn lost 2/6).

## Next

- **F:** viscosity vs extinction, registered with 12 seeds.
- **G:** a new mechanism for the learning effect on sharing. A gift reward
  reinforces the recipient's active share pathway, a learned reciprocity loop.
  It is tested by ablating the gift reward.

## Update (Experiment J, 2026-10-15)

When the locomotion input weights are frozen, the learning effect on sharing
disappears ([J](FINDINGS_J.md)). The extra sharing under learning is best
explained as a side effect of locomotion weights weakening, not as learned
sharing.
