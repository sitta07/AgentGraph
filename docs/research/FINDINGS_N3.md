# Findings: Experiment N3 — left/right flips do not hurt foraging, so the shift test fails again

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds
(1500–1511, never run before) × 12000 ticks. Viscous. Left/right sensing
flips every 2000 ticks. Pre-registered at commit `2663ed3`, spec unchanged,
no deviations. Report:
[`results/N3_repeated_shifts/`](../../results/N3_repeated_shifts/REPORT.md).

**Measure.** `shift_drop` is food per agent-tick in the 500 ticks before each
flip minus the 500 ticks after it, averaged over the 5 flips.

| Hypothesis | Test | Result |
|---|---|---|
| H30a: manipulation check, foraging drops after a flip (learning) | +0.0004 [−0.0008, 0.0018] | not supported |
| H30b: manipulation check, foraging drops after a flip (no learning) | −0.0014 [−0.0022, −0.0006] | not supported (foraging slightly *rises*) |
| H30c: learning shrinks the drop | +0.0019 [0.0006, 0.0034] | not supported (the reverse) |
| H30d: Lamarckian populations suffer a larger drop | +0.0008 [−0.0015, 0.0029] | not supported |
| H30e: Lamarckian populations die out sooner | −2083 [−3956, −349] ticks | **supported** |

| condition | extinct | food before flip | food after flip | attack rate |
|---|---|---|---|---|
| darwin | 2/12 | 0.0342 | 0.0338 | 0.148 |
| lamarck | 5/12 | 0.0322 | 0.0309 | 0.394 |
| darwin_nolearn | 0/12 | 0.0448 | 0.0463 | 0.015 |

## Interpretation

- **Swapping left and right is not a real challenge in this world.** Agents
  with fixed, evolved wiring ate slightly *more* after each flip. Learning
  agents showed no measurable drop. So H30c and H30d cannot be interpreted:
  there is no drop to buffer or to make worse.
- One likely reason is that the evolved sensor-to-action wiring is close to
  left/right symmetric, or that foraging relies mostly on moving forward when
  food is ahead. Then mirroring changes little. This was not checked before
  registering, and it should have been: N had already failed its manipulation
  check. **Lesson recorded:** run a manipulation pilot before registering an
  environment-shift test.
- **Lamarckian populations died sooner again.** This is the third time (N post
  hoc, N2 pre-registered, N3 pre-registered). Extinctions were 5/12 vs 2/12
  here, a smaller gap than N2's 9/12 vs 1/12. Because the shift itself had no
  effect, this result is about Lamarckian inheritance in general, not about
  coping with change.
- The foraging cost of learning appears again, and it is the same size as in
  P: learners ate 0.034 per agent-tick against 0.045 without learning.

## Next step

To test learning and inheritance under environmental change, choose a shift
that measurably hurts fixed-wiring agents in a pilot. For example: move food
into a region that agents must find, or reverse which sensor signals danger
versus food.
