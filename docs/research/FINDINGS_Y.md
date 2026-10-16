# Findings: Experiment Y — learning pays after only 150 ticks of practice, so short lives do not fully explain X

**Status:** completed 2026-10-17. 60 runs: 5 training budgets × 12 training
seeds (800–811), each agent tested on 16 held-out worlds (9200–9215). Seeds
and worlds had never been run. Single agents with the W "full" dynamics
(32 ms decisions, state cleared before each decision, normalised weights),
500-tick test episodes. Pre-registered at commit `89f6310`, spec unchanged,
no deviations. A 6-seed pilot on other seeds preceded registration. Run time
24 min. Report: [`results/Y_learning_budget/`](../../results/Y_learning_budget/REPORT.md).

**Question.** In [X](FINDINGS_X.md), learning did not pay in evolving
populations, and a rough estimate put the mean lifetime there at about 150
ticks. Does learning simply need more practice than that?

| Hypothesis | Test | Result |
|---|---|---|
| H42a: after 1500 ticks, learning pays | +12.2 [9.5, 14.5] food per episode | **supported** |
| H42b: 1500 ticks beats 150 ticks | +11.2 [8.4, 13.8] | **supported** |
| H42c: after 150 ticks, learning pays | +0.94 [0.45, 1.42] | **supported** (predicted not) |
| H42d: after 500 ticks, learning pays | +5.9 [4.6, 7.2] | **supported** |
| H42e: 20000 ticks beats 1500 ticks | +3.4 [1.4, 5.8] | **supported** |

**By the pre-registered rule (H42c had to fail), short lives do not fully
explain X's null result.** A single agent gains from as little as 150 ticks
of practice.

| training budget (ticks) | trained food | trained, scrambled senses | untrained | per-seed range |
|---|---|---|---|---|
| 150 | 4.56 | 3.52 | 3.62 | 3.1–5.8 |
| 500 | 9.51 | 3.51 | 3.62 | 5.4–13.7 |
| 1500 | 15.77 | 3.24 | 3.62 | 7.1–20.6 |
| 5000 | 17.57 | 2.94 | 3.62 | 12.7–21.6 |
| 20000 | 19.21 | 3.14 | 3.62 | 14.2–21.1 |

## Interpretation

- **Learning with the fixed dynamics is fast.** Most of the gain comes in the
  first 1500 ticks (three episodes). After 500 ticks agents eat 2.6× more than
  untrained ones. Every gain disappears when the senses are scrambled, so the
  learned behaviour is sensory foraging at every budget.
- **At 150 ticks the gain is real but small,** +0.94 food per 500-tick
  episode (+26%). In X, learning populations ate +6% more than non-learning
  ones (+0.0020 [−0.0028, 0.0062] per agent-tick), a difference the study
  could not resolve. The two results do not contradict each other, but Y
  shows that short lives are not the whole story.
- **The pilot misled on the shortest budget.** On 6 seeds and 8 worlds it
  showed a loss at 150 ticks (−1.31). On 12 fresh seeds and 16 worlds the
  effect is a gain. The rest of the curve replicated.
- **What else could block learning in populations (not tested):** attacks
  and theft from other agents add reward and punishment unrelated to
  foraging; 24 food items are shared by about 35 agents; and the 150-tick
  lifetime is a rough mean, so many agents live much less.

## Limits

- Single agents in a non-social world. The training budget is the only
  thing varied; social reward noise is absent.
- The lifetime in X is an estimate from birth counts, not a measured
  distribution.

## Next step

Measure the lifetime distribution in X directly, and test learning in a
social world without evolution (fixed population, no births or deaths), so
lifetime and social noise can be separated.
