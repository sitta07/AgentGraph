# Findings: Experiment L — what differs before well-mixed populations collapse?

**Status:** completed 2026-10-16. 32 runs: 2 conditions × 16 seeds (500–515,
never run before) × 18000 ticks. Pre-registered at commit `a2ce17c`, spec
unchanged, no deviations. Report:
[`results/L_collapse_demography/`](../../results/L_collapse_demography/REPORT.md).

All demographic metrics are measured over **ticks 0–6000**, before any
population had died out. That avoids the confound found in F2's H17.

| Hypothesis | Test (mixed − viscous) | Result |
|---|---|---|
| H21a: lower birth rate in well-mixed populations | −0.0009 [−0.0015, −0.0003] per agent-tick (0.0027 vs 0.0036) | **supported** |
| H21b: more of the well-mixed deaths are killings | −0.083 [−0.133, −0.034] (58% vs 67%) | not supported, **opposite direction** |
| H21c: more of the well-mixed deaths are starvation | +0.065 [0.031, 0.098] (37% vs 31%) | **supported** |
| H21d: fewer well-mixed offspring reproduce | +0.046 [0.034, 0.060] (19% vs 14%) | not supported, **opposite direction** |
| H14b3: well-mixed populations die out sooner (third test) | −3916 ticks [−6379, −1490] | **supported** |

Extinctions: **11/16 well-mixed vs 5/16 viscous** (Fisher p = 0.076
two-sided). Over the three independent runs (F fresh seeds, F2, L), well-mixed
populations died first every time. The extinction *count* was never decisive
alone, but the survival-time difference replicated in all three.

## What the early demography shows

| (ticks 0–6000) | well-mixed | viscous |
|---|---|---|
| births per agent-tick | 0.0027 | 0.0036 |
| deaths per agent-tick | 0.0026 | 0.0035 |
| deaths that were killings | 58% | 67% |
| deaths from starvation | 37% | 31% |
| deaths from old age | 5% | 3% |
| offspring born before t=4500 that reproduced | 19% | 14% |

## Interpretation

- **Killing is the main cause of death in both worlds** (58–67%). Very few
  agents reach old age.
- **Viscous populations turn over faster.** Births and deaths are both about
  33% more frequent, and a larger share of deaths are killings. Each newborn
  is *less* likely to reproduce, yet the population as a whole produces more
  births.
- **Well-mixed populations run slower and hungrier.** Fewer births, a larger
  share of starvation deaths, and a lower birth rate per agent. A population
  whose birth rate is barely above its death rate has a smaller margin, so
  chance runs of deaths are more likely to end it.
- **Food patches cannot explain it.** Food respawns uniformly at random, so
  a newborn next to its parent is not in a richer area.
- **What viscous placement does change:** newborns start next to *someone*,
  and that someone is a relative. Energy can then move locally, through
  theft and sharing among neighbours, and the faster turnover follows.
- **Two candidate explanations, not yet separated:** relatedness (kin
  structure) or local density (being near anyone). Experiment Q separates
  them by placing well-mixed newborns next to a random unrelated agent.

## Limits

- Cause-of-death is inferred: deaths with a killing event are "killed",
  deaths at `max_age` are "old age", and every other death is "starved".
- An agent born and killed within the same tick is not counted.
- One ecology with learning on. We did not test whether this holds without
  learning.
