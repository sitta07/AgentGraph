# Findings: Experiment AL — with invisible hazards, still no fear-like state, and selection shortened persistence

**Status:** completed 2026-10-17. 24 runs: 2 conditions × 12 seeds
(3700–3711, never run before) × 18000 ticks. Learning off. Pre-registered at
commit `7637c20`, spec unchanged, no deviations. No pilot. Run time 94 min.
Report: [`results/AL_invisible_hazards/`](../../results/AL_invisible_hazards/REPORT.md).

**Question.** [AK](FINDINGS_AK.md) found no emotion-like states evolving.
One reason could be that its decision network already sees hazards, so an
internal state has nothing to add. AL makes the threat sensors always read 0
(`hazards_visible=False`). The only route by which being hurt can change
behaviour is then the evolved internal state, whose inputs include pain. AL
also halves the mutation step (0.15).

| Hypothesis | Test (affect − numb) | Result |
|---|---|---|
| H59a: acting affect, longer survival | −1254 [−3412, 425] ticks | not supported |
| H59b: acting affect, more food per agent-tick | −0.0066 [−0.0133, −0.0004] | not supported (lower) |
| H59c: larger response right after a pain pulse | −0.030 [−0.100, 0.035] | not supported |
| H59d: longer-lasting response after the pain has passed | −0.061 [−0.130, −0.009] | not supported (shorter) |
| H59e: longer memory (decay) | −0.078 [−0.242, 0.060] | not supported |

**By the pre-registered rule, no pain-responsive state evolved under
selection (H59c not supported), and the acting state was not adaptive.**

| condition | extinct | mean survival | food per agent-tick | max generation | persistence | decay | pain–food cosine |
|---|---|---|---|---|---|---|---|
| affect (state acts) | 3/12 | 15975 | 0.030 | 50 | 0.048 | 0.46 | −0.08 |
| numb (state never acts) | 3/12 | 17229 | 0.037 | 33 | 0.073 | 0.55 | +0.37 |

## Interpretation

- **Even when pain could reach behaviour only through the evolved state,
  selection did not build a stronger pain response.** The immediate response
  matched drift.
- **Selection shortened persistence.** Responses lasting past the pain were
  shorter in acting populations than in drifted ones (CI excludes zero), and
  decay was lower, although that difference is not significant. A lingering
  state was, if anything, selected against. One reading, untested: with no
  memory elsewhere, a state that keeps pushing actions after the cause has
  gone mostly adds noise to foraging.
- **The acting state again lowered foraging,** by about 18% (0.030 vs
  0.037). This replicates the direction of AK.
- **Pain and food came to push behaviour in more opposite directions in
  acting populations** (cosine −0.08 vs +0.37). This is a valence-like
  pattern, but it was not a pre-registered test in AL and is noted only as a
  lead.

## Limits

- Different generation counts across conditions (50 vs 33), as in AK.
- The assay runs in an empty arena. It measures what the state does to
  behaviour, not whether it helps avoid hazards in the world.
- Functional criteria only. Nothing here bears on subjective experience.

## Next step

Across AK and AL, a free-form internal state has not paid in this world. Two
directions remain open:

- A world where persistence clearly pays, for example hazards that stay
  dangerous for a while after contact, or predators that return. Then test
  for a fear-like state again.
- Test the valence lead with a pre-registered study.
