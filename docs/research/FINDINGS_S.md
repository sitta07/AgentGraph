# Findings: Experiment S — requiring a partner to eat did not give signals meaning

**Status:** completed 2026-10-16. 24 runs: 2 conditions × 12 seeds
(1400–1411, never run before) × 18000 ticks. Viscous, learning off. One
`deaf` population went extinct (at tick 17453). Pre-registered at commit
`4e69dea`, spec unchanged, no deviations. Report:
[`results/S_signals_with_a_reason/`](../../results/S_signals_with_a_reason/REPORT.md).

**Design.**
- Food can be eaten only if another living agent is within 0.15
  (`coop_radius`).
- Hearing is directional: three extra sensors tell a listener which side a
  call came from.
- In `deaf`, all hearing sensors read 0, so signals cannot affect anyone.
- Learning is off, so only selection shapes signalling.

| Hypothesis | Test (hearing − deaf) | Result |
|---|---|---|
| H29a: signals carry more information about food in view | −0.00002 [−0.00010, 0.00008] bits | not supported |
| H29b: hearing populations survive longer | +46 [0, 137] ticks | not supported |
| H29c: hearing populations eat more | +0.0009 [−0.0006, 0.0024] | not supported |
| H29d: hearing populations signal more | −0.0024 [−0.0036, −0.0009] | not supported (the reverse) |

## Interpretation

- **Same result as M.** Signals carry about 0.0002–0.0003 bits about food,
  threat or hunger, with or without hearing. The added need for a partner did
  not change that within ~14 generations.
- **The partner rule did bind, so this is a real negative result.** S did not
  measure blocked food. A follow-up pilot (unregistered seed 9996, ticks
  0–4000, same settings) added `food_blocked_frac`: 42% of the food that
  agents reached was blocked because no partner was within 0.15. Well-mixed
  populations gave 38%; a radius of 0.10 blocked 74%. So eating did depend
  on having a partner, and signals still did not come to carry information
  about food.
  - An earlier draft of this page guessed that the rule did not bind,
    because encounters within 0.08 were common (48% of ticks). The pilot
    contradicts that guess.
- Possible reasons, untested:
  - any agent can serve as a partner, so a call about food helps no more
    than staying near others;
  - without learning, about 14 generations of selection may be too few;
  - a single binary call neuron may be too coarse to carry a code.

## Also observed (not pre-registered)

- Hearing populations signalled less (0.0075 vs 0.0099). They also shared
  less given a neighbour in reach (−0.0030 [−0.0041, −0.0021]) and tended to
  attack less (−0.014 [−0.033, 0.001]).
  - One possible reason: heard calls feed into every action population, and
    selection damps that extra input. Untested.
- Hearing changed what listeners did by a measurable but tiny amount: the
  mutual information between hearing a call and the next action was 0.0001
  to 0.0008 bits. The G-test was "significant" in 12/12 runs. As M showed,
  that says little at these sample sizes.
- `innate_foraging` is 0 in both conditions because the single-agent
  foraging test cannot eat alone under the partner rule. The metric does not
  apply to this world.

## Next step

A future signalling study should make the benefit specific to the caller.
For example, food that only the caller can see, so that a listener must
reach it. It should also log `food_blocked_frac` as a manipulation check.
