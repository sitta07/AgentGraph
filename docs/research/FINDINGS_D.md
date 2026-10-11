# Findings: Experiment D — does a heritable aggression gene evolve under scarcity?

**Status:** completed 2026-10-12. 12 runs: 2 conditions × 6 seeds × 8000
ticks. No population went extinct. The study was pre-registered at commit
`589e709` and the spec was unchanged when it ran. Report:
[`results/D_scarcity_aggression/`](../../results/D_scarcity_aggression/REPORT.md).

| Hypothesis | Test (scarce − abundant) | Result |
|---|---|---|
| H8: the aggression gene evolves higher under scarcity | +0.75 [0.37, 1.04] (1.86 vs 1.11) | **supported** |
| H8b: agents attack more often under scarcity | +0.001 [−0.031, 0.037] (13.5% vs 13.4%) | not supported |
| H8c: more attacks when a neighbour is in reach | +0.006 [−0.022, 0.040] | not supported |

## Why H8 is not yet evidence of selection

1. **The gene had no behavioural effect.**
   - Attack rates were identical in both worlds.
   - The gene only scales a *frustration*-driven current, and frustration
     stays low when rewards are scarce: expectations adapt, as in our earlier
     lifetime study.
   - A trait that does not change behaviour cannot be selected.
2. **Scarce worlds ran through more generations** (19 vs 8) because lifespans
   were shorter.
   - More generations means more opportunity for **genetic drift** of a
     mutating trait.
   - The mutation operator also clips the gene at zero, which can introduce a
     small upward bias.

So the pre-registered H8 passed, but the data are equally consistent with drift.

## Follow-up: D2 with a neutral marker

D2 is pre-registered in `studies/`. Every agent carries a **neutral marker
gene** that is inherited, mutated and clipped exactly like the aggression
gene but has no effect. If aggression rises *more than the neutral marker*
under scarcity, that points to selection. If both rise equally, the H8 result
is drift.

## Follow-up result: D2 (completed 2026-10-12)

D2 ran 16 runs: 2 conditions × 8 seeds × 8000 ticks, with a neutral marker
gene. It was pre-registered and run without deviations. One scarce
population went extinct. Report:
[`results/D2_aggression_vs_neutral_marker/`](../../results/D2_aggression_vs_neutral_marker/REPORT.md).

| Hypothesis | Test | Result |
|---|---|---|
| H16: under scarcity the aggression gene exceeds the neutral marker | −0.20 [−0.74, 0.24] | not supported |
| H16b: the excess is larger under scarcity than abundance | −0.34 [−0.86, 0.10] | not supported |
| H16c: the neutral marker is higher under scarcity (drift) | +0.08 [−0.26, 0.47] | not supported |

**Conclusion:**

- In D2 the aggression gene under scarcity averaged ≈0.96. It was not
  elevated, and it was indistinguishable from the neutral marker.
- D's H8 result (1.86) did **not** replicate. It is best explained as chance
  or drift in a small sample.
- **There is no evidence that aggression is selected under scarcity in this
  world.** That is consistent with the gene having had no effect on attack
  behaviour in D.
