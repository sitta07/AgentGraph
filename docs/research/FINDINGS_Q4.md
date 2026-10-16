# Findings: Experiment Q4 — any move away from the parent removes most of viscosity's protection, with no further dose-response

**Status:** completed 2026-10-16. 48 runs: 4 conditions × 12 seeds
(1900–1911, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `cb7cba9`, spec unchanged, no deviations. No pilot. Run time 95 min.
Report: [`results/Q4_dispersal_distance/`](../../results/Q4_dispersal_distance/REPORT.md).

**Intervention.** `birth_distance=d` places each newborn exactly `d` from its
parent in a random direction (reflected at walls). Default viscous placement
scatters newborns with s.d. 0.04 per axis. No stranger is involved.

| Hypothesis | Test (a − b) | Result |
|---|---|---|
| H34a: far (0.45) placement dies out sooner than viscous | −1458 [−3378, 621] ticks | not supported |
| H34b: far placement goes extinct more often than viscous | +0.42 [0.00, 0.75] | not supported (lower bound at 0) |
| H34c: dose-response, far dies out sooner than near (0.15) | +928 [−1270, 3101] ticks | not supported (if anything, the reverse) |
| H34e: spread lowers the early birth rate (far vs viscous) | −0.00069 [−0.0011, −0.0003] | **supported** |

**By the pre-registered rule (H34a and H34c), spread is not supported as a
cause with a dose-response.**

## Extinction counts and demography (not pre-registered)

| condition | extinct | mean survival (ticks) | early birth rate | kills of own offspring | starvation share of deaths | final population |
|---|---|---|---|---|---|---|
| viscous (s.d. 0.04) | **2/12** | 17415 | 0.0032 | 40% | 32% | 27.1 |
| near (0.15) | **8/12** | 15028 | 0.0026 | 13% | 37% | 11.7 |
| far (0.45) | 7/12 | 15956 | 0.0026 | 4% | 40% | 13.2 |
| mixed (random) | 10/12 | 13582 | 0.0029 | 4% | 38% | 3.5 |

Fisher exact (two-sided, not pre-registered): viscous vs near p = 0.036;
viscous vs far p = 0.089; viscous vs mixed p = 0.003; near vs far p = 1.0.

## Interpretation

- **The protection is lost at the first step away from the parent.**
  Moving newborns 0.15 away (a quarter of the sensor range) raised
  extinctions from 2/12 to 8/12. Moving them three times further did not
  make things worse. The effect looks like a threshold, not a gradient. That
  is why the pre-registered dose-response test (H34c) failed while the
  extinction counts differ strongly. The threshold reading is post hoc.
- **Viscosity's protection replicated a fourth time** (viscous vs mixed:
  2/12 vs 10/12, p = 0.003).
- **What all harmful placements share is that the newborn does not start next
  to its own parent.** Stranger placement (Q–Q3) keeps a neighbour but
  removes the parent. Near and far placement here remove both. Random
  placement removes both. Spatial spread over the whole world is not
  required: 0.15 is enough.
- **Killing of offspring follows proximity, and it is not what hurts.** Parents
  killed their own offspring in 40% of kills in viscous worlds, 13% at 0.15
  and 4% at 0.45. Yet the viscous worlds, with the most filial killing,
  survived best. This fits Q3, where removing the energy gain from those
  kills did not shorten survival.
- Dispersal lowered the early birth rate (H34e). Births per agent-tick fell
  by about a fifth. That alone may not explain extinction: in Q3 a similar
  drop from `no_filial_gain` did not raise extinctions.

## What this rules out, and what is left

Ruled out as the whole explanation so far: local density (Q), strangers
killing newborns (Q2), parents recycling energy (Q3), and gradual spatial
spread (Q4). Still open, untested:

- **Parent-specific effect.** Something about starting next to the parent
  itself, not next to relatives in general. Test: place newborns beside a
  random living relative other than the parent (sibling or cousin) at the
  viscous distance.
- **Kin clusters and local competition.** Viscous worlds form clusters of
  relatives (60% of kills are on kin, vs 33–43% otherwise). The scale of
  competition may matter separately from relatedness (Griffin, West &
  Buckling 2004; see [`LITERATURE_NOVELTY.md`](LITERATURE_NOVELTY.md)).
- **Study V** (registered at `5e396d5`) asks whether these agents use their
  senses at all. If they do not, local position matters only through who is
  nearby, which narrows the candidates above.
