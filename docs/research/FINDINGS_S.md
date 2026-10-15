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
- **The partner requirement probably did not bind.** Populations are viscous,
  and an agent had a neighbour within 0.08 on 48% of ticks. A partner within
  0.15 is therefore usually present without any coordination. Food per
  agent-tick (0.044) was close to normal worlds. So there was still little
  reason to call others. This is the most likely reason S failed as a test.
  The manipulation was not checked in advance; a direct measure (the share
  of food blocked by the partner rule) would have caught it.

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

Before another signalling study, make the partner rule bind and check it
with a manipulation measure. For example: well-mixed placement or a lower
density, and log how many food items are blocked for lack of a partner.
