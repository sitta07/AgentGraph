# Findings: can spiking agents learn aggression or cooperation within one lifetime?

**Status:** completed study, 2026-10-12 · raw data and the auto-generated report:
[`results/social_lifetime/`](../../results/social_lifetime/REPORT.md) ·
reproduce with `python -m neuralmind.research.social all --seeds 10`

## Question

Five agents share an arena. Each agent's brain is a small spiking network that
can choose to move, **attack** (steal energy from a neighbour), **share** (give
energy; the recipient gets twice as much) or **signal**. We asked four
pre-registered questions. Each verdict counts as "true" only when the 95%
bootstrap CI excludes zero:

| | Hypothesis | Verdict |
|---|---|---|
| H1 | Food deprivation increases attacks | not supported |
| H2 | …and that increase runs through the frustration→attack pathway (ablation) | not supported |
| H3 | Scarce food increases attacks | not supported (per-tick rate) |
| H4 | Kinship weight (Hamilton's r·B > 1) increases sharing | not supported |

## What we actually learned

### 1. A modelling artifact produced convincing fake "aggression"

The pilot model (v1) computed the frustration variable from the reward
prediction error of the full learning reward, including the
alignment-shaping term. Under v1 the agents looked strongly aggressive while
fed: 12.7% [8.1, 17.2] of agent-ticks were attacks. Attacks then collapsed
under deprivation (−12.6 percentage points, CI excludes 0).

That looked like a real result. The ablation showed it was not:

- With the frustration→attack pathway cut, attacks were only 0.19%.
- The "aggression" was driven by noise in the shaping term, which is not a
  biological signal.
- Deprivation reduced it because removing food also removes the shaping noise.

**Fix (v2):** affect is now computed from the *primary* reward only (eating,
hazards, theft, being hurt). v1 is kept as `affect_from_primary=False` so the
artifact can be reproduced.

> Lesson: an internal variable with an emotional label can produce
> plausible-looking behaviour for an uninteresting reason. Without the ablation
> this would have been reported as "hungry agents calm down".

### 2. Social behaviour does not emerge from within-lifetime learning alone

Under v2:

- Attacks are rare (≈0.2% of agent-ticks).
- **Attacks given that another agent is within reach are ≈0%.** In other
  words, attacks are untargeted misses.
- Sharing is rare at every kinship level.

Each agent gets only a few hundred ticks. Social opportunities, meaning
another agent in reach, occur in ≈10% of them. A social action that is
sampled almost never is also reinforced almost never. This is an exploration
bottleneck, well known in multi-agent RL. Here we observed it directly in a
biologically-inspired learner.

### 3. One small secondary effect

Conditioned on an encounter, scarce worlds produced slightly more attacks than
abundant ones: +2.7 percentage points [0.6, 5.2]. This was **not** a
pre-registered primary measure and several secondary measures were inspected,
so we treat it as *exploratory*.

## Why this matters / next step

These negative results are informative. They suggest that social behaviour in
such agents needs a slower adaptive process acting across lifetimes.
**Evolution** is the obvious candidate: weights inherited with mutation and
selection by survival and reproduction. With offspring born near their
parents, kinship becomes a *real genealogical quantity* rather than an imposed
reward weight. That makes Hamilton's rule genuinely testable.

That is the next experiment in this repository.
