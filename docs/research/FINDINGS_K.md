# Findings: Experiment K — it is the weakening of locomotion that frees social actions

**Status:** completed 2026-10-15. 24 runs: 3 conditions × 8 seeds (400–407,
never run before) × 8000 ticks. No population went extinct. Pre-registered at
commit `98a188f`, spec unchanged, no deviations. Report:
[`results/K_locomotion_normalized/`](../../results/K_locomotion_normalized/REPORT.md).

**Question.** In Experiment J we froze locomotion learning entirely, and
learned social behaviour disappeared. But freezing also removed foraging
learning, so J could not tell *weakening* apart from other foraging changes.

**Intervention.** In `loco_norm` the locomotion input weights keep learning,
so weight can move between sensors. After every update, each locomotion
neuron's total input is rescaled to its innate sum, so locomotion cannot get
weaker overall.

| Hypothesis | Test | Result |
|---|---|---|
| H20a: fixed locomotion sums lower attacks | learn_all − loco_norm = +0.117 [0.065, 0.197] | **supported** |
| H20b: … lower signalling | +0.013 [0.007, 0.019] | **supported** |
| H20c: … lower sharing (neighbour in reach) | +0.0064 [0.0044, 0.0083] | **supported** |
| H20d: with fixed sums, learning no longer raises attacks | loco_norm − nolearn = +0.006 [−0.003, 0.015] | no difference detected |
| H20e: with fixed sums, learning no longer raises signalling | +0.0009 [0.0003, 0.0015] | **difference detected** (small) |

How much of the learning effect is left when locomotion sums are held fixed
(loco_norm − nolearn, divided by learn_all − nolearn):

| behaviour | learning effect | left over | removed |
|---|---|---|---|
| attack rate | 0.123 | 0.006 | ~95% |
| signal rate | 0.0137 | 0.0009 | ~93% |
| share \| neighbour | 0.0081 | 0.0016 | ~80% |

## Interpretation

- **The weakening is the cause.** Locomotion inputs could still learn here;
  only their total strength was held fixed. That removed 80–95% of the
  learning-induced rise in every social behaviour. Together with I and J,
  this pins the effect on one mechanism: reward-modulated learning lowers
  total locomotion drive, so social action populations win the spike-count
  competition more often.
- A small residue remains: about 7% for signalling and 20% for sharing, and
  both are significant. Some genuinely reward-driven change, such as the
  gift-reward loop from G, may account for it.

## Side observations (not pre-registered)

- Learning populations without the constraint went through more generations
  (12.4 vs 7.3 without learning). With locomotion sums fixed they did not
  (6.5). More attacking means more turnover, which may explain this.
- Under the constraint, innate foraging did not differ from no-learning
  (−1.8 [−4.5, 1.3]). The hiding effect was weaker here than with
  unconstrained learning.

## Limits

- Rescaling after every update is a strong, non-biological constraint. It
  shows that the drop in total locomotion drive is necessary for the effect.
  It does not explain why reward-modulated learning lowers that drive.
- The rescaled weights are not re-clipped to `w_max` (4.0). The innate sums
  are about 1.2 × 11 per row, so a single weight is unlikely to come near
  that limit, but we did not check it.
- One ecology, viscous populations, 8 seeds.

## Exploratory: why does locomotion drive fall?

[`drift_probe.py`](../../neuralmind/research/drift_probe.py) logs every
update `lr · RPE · eligibility` and splits it by tick type. We ran 3
unregistered seeds (900–902) for 2000 ticks each.

**Totals per seed.** Units are summed over all agents and synapses, so only
the sign and the relative size within a seed are meaningful.

| | seed 900 | seed 901 | seed 902 |
|---|---|---|---|
| locomotion, eating ticks | +2071 | +1588 | +1844 |
| locomotion, pain ticks | −2120 | −1727 | −2182 |
| locomotion, shaping-only ticks | −2465 | −3274 | −3220 |
| social, all ticks | −442 | −317 | −231 |
| updates with negative RPE | 59% | 57% | 58% |
| locomotion / social eligibility | 8.7× | 8.1× | 8.5× |

**What the probe shows.**

- The reward predictor's baseline includes rare, large food rewards, so on
  most ticks the RPE is negative. This is true even when agents are only
  receiving the small shaped reward.
- The eligibility rule is potentiation-only, and its trace scales with how
  much a population fires.
- Locomotion fires about 8× more than the social populations. It therefore
  absorbs most of those negative updates.

**Candidate mechanism (untested).** The learning rule produces
activity-dependent depression: the most-used pathways weaken most, which
hands action-selection share to rarely used actions. This is a hypothesis
from three exploratory seeds, not a confirmed result. A pre-registered test
would subtract a per-population activity baseline from the eligibility, or
use a zero-mean RPE, and predict that the social rise disappears.
