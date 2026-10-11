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
