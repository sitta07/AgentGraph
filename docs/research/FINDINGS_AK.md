# Findings: Experiment AK — no emotion-like states evolved; an acting internal state lowered foraging

**Status:** completed 2026-10-17. 24 runs: 2 conditions × 12 seeds
(3600–3611, never run before) × 18000 ticks. Learning off. Pre-registered at
commit `0fabb50`, spec unchanged, no deviations. No pilot (1500-tick smoke
runs only). Run time 92 min.
Report: [`results/AK_evolved_affect/`](../../results/AK_evolved_affect/REPORT.md).

**Question.** Anderson & Adolphs (2014) proposed that emotion states share
measurable "emotion primitives", among them persistence, scalability and
valence. Gibson et al. (2015) used such tests on flies. Here no emotion was
designed in. Each agent carries two internal state variables, `s`:

- every tick, `s ← decay · s + A · inputs`, with five inputs: pain, food
  eaten, hunger, threat in view, others in view
- `Bᵀ · s` is added to the input current of every action
- A, B and the decays start at zero (decay 0.5) and mutate at every birth

The decision network has no memory of its own, so this state is its only
memory. In the numb control the same genes evolve, but the state never acts.
The designer's frustration drive was off and learning was off. An assay in
an empty arena compared behaviour after a one-tick pulse with an identical
run without it.

| Hypothesis | Test (affect − numb) | Result |
|---|---|---|
| H58a: acting affect, longer survival | −2458 [−6018, 635] ticks | not supported |
| H58b: acting affect, more food per agent-tick | −0.012 [−0.021, −0.002] | not supported (lower) |
| H58c: longer persistence after a pain pulse | +0.003 [−0.068, 0.111] | not supported |
| H58d: more scalability | −0.029 [−0.087, 0.027] | not supported |
| H58e: more opposite valence | −0.17 [−0.68, 0.19] | not supported |
| H58f: longer memory (decay) | −0.055 [−0.182, 0.085] | not supported |

**By the pre-registered rule, emotion-like states did not evolve under
selection (H58c not supported), and the acting state was not adaptive (H58a,
H58b not supported).**

| condition | extinct | mean survival | food per agent-tick | max generation | output weight size | decay |
|---|---|---|---|---|---|---|
| affect (state acts) | 4/12 | 13839 | 0.024 | 34 | 18.3 | 0.50 |
| numb (state never acts) | 6/12 | 16297 | 0.038 | 9 | 11.3 | 0.57 |

## Interpretation

- **The evolved internal state behaved like noise, not like an emotion.**
  Its assay scores matched those of drifted genes. Its decay stayed at the
  starting value (0.50 vs 0.57).
- **Letting the state act lowered foraging by about 37%** (0.024 vs 0.038,
  CI excludes zero). Random mutations of A and B add arbitrary currents to
  the actions, and in 18000 ticks selection did not tune them into
  something useful.
- **Affect populations turned over faster** (34 generations vs 9). Their
  genes therefore had more mutations, which shows in the larger output
  weights (18 vs 11). This makes "selected minus drifted" comparisons
  unequal, and the assay contrasts should be read with that in mind.
- **What this does and does not show.** It does not show that emotion-like
  states cannot evolve here. It shows that, with this design, they did not
  in 18000 ticks. Possible reasons, none tested:
  - The mutation step (0.3 on every gene) is large relative to any useful
    setting.
  - The selective value of a one-variable memory is small in this world.
  - The run is too short for selection to tune nine genes per state.

## Limits

- The assay ran on 8 affect and 6 numb populations (the others went extinct).
- Different generation counts across conditions; see above.
- "Emotion-like" here means a functional internal state that meets
  behavioural criteria. Nothing in this study bears on subjective experience.

## Next step

Give selection a reason and a chance:

- a world where memory pays, for example hazards that move or food that
  appears where a warning was seen
- smaller mutation steps
- longer runs
- a generation-matched drift control (the neutral gene used in [AH](FINDINGS_AH.md))
