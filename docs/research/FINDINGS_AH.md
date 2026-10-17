# Findings: Experiment AH — an evolving teacher lengthens survival, and evolution turns approach shaping down

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(3400–3411, never run before) × 18000 ticks. Learning on, fixed dynamics.
Pre-registered at commit `d4398fd`, spec unchanged, no deviations. Run time
138 min, part of it sharing the machine with AI, AJ and AK.
Report: [`results/AH_evolved_teacher/`](../../results/AH_evolved_teacher/REPORT.md).

**Question.** Following Singh, Lewis & Barto (2009) and Niv et al. (2002),
the shaping part of the learning reward was made heritable. Each agent
carries four teacher weights on four signals:

- change in alignment with the nearest food
- decrease in distance to it
- change in its own energy
- hunger

The weights mutate by N(0, 0.5) at every birth. A neutral gene mutates the
same way and is never read, as a drift baseline. There are three conditions:

- *designer*: fixed default teacher
- *evolved*: starts from the default teacher
- *evolved_scratch*: starts from all zeros

| Hypothesis | Test | Result |
|---|---|---|
| H56a: evolving teacher eats more than designer | −0.006 [−0.014, 0.005] food per agent-tick | not supported |
| H56b: evolving teacher survives longer than designer | +3089 [62, 6131] ticks | **supported** |
| H56c: approach weight rises more than the neutral gene | −4.83 [−6.68, −2.91] (n = 5) | not supported (opposite direction) |
| H56d: energy weight falls more than the neutral gene | +3.70 [−0.07, 7.34] (n = 5) | not supported |
| H56e: evolving teacher shares more | +0.0002 [−0.019, 0.022] | not supported |
| H56f: teacher from scratch differs in foraging from designer | +0.010 [0.003, 0.018] | **difference detected** |

**By the pre-registered rule, evolution designs a better teacher in the
sense of survival (H56b), not foraging (H56a).** Of the teacher weights,
only the approach weight moved beyond drift, and it moved *down*.

| condition | extinct | mean survival | food per agent-tick | attack rate | max generation |
|---|---|---|---|---|---|
| designer | 9/12 | 11630 | 0.032 | 0.36 | 17 |
| evolved (from designer) | 7/12 | 14720 | 0.028 | 0.42 | 43 |
| evolved from scratch | 7/12 | 14952 | 0.030 | 0.34 | 25 |

Final teacher weights, shift from start minus the neutral gene's shift.
These are means over the 5 runs per condition still alive at the end, with
95% bootstrap CIs:

| weight | evolved | evolved from scratch |
|---|---|---|
| alignment | −1.3 [−5.8, 3.2] | +2.8 [−0.6, 6.7] |
| approach | **−4.8 [−6.7, −2.9]** | −1.6 [−4.1, 1.0] |
| energy | +3.7 [−0.1, 7.3] | +0.6 [−2.5, 4.3] |
| hunger | −1.1 [−5.7, 5.6] | +0.3 [−2.0, 2.5] |

## Interpretation

- **Letting the teacher evolve lengthened survival** by about 3100 ticks in
  both evolving conditions. Neither ate more per agent-tick.
- **Evolution turned approach shaping down.** This contradicts the
  prediction from [AF](FINDINGS_AF.md), where approach shaping rescued
  learning among social peers. The settings differ:
  - AF: no hazards, no evolution, 1500 training ticks
  - AH: hazards, evolving populations, lifetimes of up to 1500 ticks

  Untested guess: approaching the nearest food also leads into hazards
  near food, which AF's world did not have.
- **A teacher evolved from scratch drifted toward valuing alignment**
  (+2.8 over drift, from 0 to about 3.0). The CI includes zero, so this is
  not established. It foraged slightly better than the designer teacher
  (H56f).
- **The pilot misled a fourth time.** It suggested that valuing energy loss
  would evolve. In the registered study that weight moved up, not down.

## Limits

- Only 5 of 12 runs per evolving condition survived to the end. The teacher
  weights rest on those 5, and survivors may differ from the rest.
- The designer condition went extinct more often than in earlier studies
  (9/12), which makes the survival contrast easier to win.
- Four signals is a narrow space for a teacher.

## Next step

Rerun the approach result without hazards, to test the guess that hazards
make approach shaping costly. Track teacher weights over time, not only at
the end, so that extinct runs also contribute.
