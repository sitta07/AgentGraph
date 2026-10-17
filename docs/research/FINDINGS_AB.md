# Findings: Experiment AB — in groups, removing hazards does not let social agents learn

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 training seeds
(870–881), agent 0 tested on 8 held-out worlds (9700–9707). Seeds and worlds
had never been run. Same design as [Z](FINDINGS_Z.md): 12 agents, 24 food,
fixed dynamics, 1500 training ticks, no evolution. Pre-registered at commit
`68dbe4b`, spec unchanged, no deviations. No pilot. Run time 94 min.
Report: [`results/AB_group_hazard/`](../../results/AB_group_hazard/REPORT.md).

**Question.** [AA](FINDINGS_AA.md) found that a lone social agent fails to
learn because it freezes in hazards, and learns once hazards are removed.
Does the same fix work in groups?

| Hypothesis | Test | Result |
|---|---|---|
| H47a: without hazards, learning pays among social peers | +0.26 [−2.19, 2.93] food per episode | not supported |
| H47b: removing hazards raises the learning gain among social peers | +2.3 [−1.8, 6.3] | not supported |
| H47c: without hazards, social peers gain less than non-social peers | −7.1 [−11.2, −2.9] | **supported** |
| H47d: without hazards, learning changes the attack rate (no direction predicted) | +0.092 [0.051, 0.137] | difference detected |

**By the pre-registered rule (H47a and H47b not supported), the hazard trap
does not explain why learning fails in social groups.** Other social effects
remain (H47c).

| condition | trained | trained, scrambled senses | untrained | learning gain | trained attack rate | untrained attack rate |
|---|---|---|---|---|---|---|
| social12, hazards | 9.0 | 8.0 | 11.0 | −2.0 | 0.13 | 0.08 |
| social12, no hazards | 15.0 | 12.4 | 14.8 | +0.3 | 0.16 | 0.07 |
| crowd12 (non-social), no hazards | 24.7 | 16.8 | 17.4 | +7.3 | — | — |

## Interpretation

- **Z replicated on new seeds.** With hazards, learning among social peers
  gave −2.0 (Z: −2.8). Among non-social peers it paid (+7.3 here, +6.9 in Z).
- **Alone and in groups, the social agent fails for different reasons.**
  Alone, hazards were the main problem (AA). In groups, removing hazards
  raised food for trained and untrained agents alike, so the learning gain
  stayed near zero.
- **In groups, learning more than doubles the attack rate** (0.07 → 0.16
  without hazards). In Z, the same rise appeared with `steal=0`, where an
  attack gains nothing. So attacks do not rise because they pay. A candidate,
  untested: other agents are often near when food is eaten, so the "other
  agent" sensors are active at rewarded moments and their pathway to the
  attack neurons is strengthened.
- Scrambling the senses still cost trained social agents 2.6 food without
  hazards, so they use their senses somewhat.

## Limits

- 1500 training ticks, fixed group, agent 0 only, 8 test worlds.
- The attack candidate is untested; the weights from "other agent" sensors
  were not inspected.

## Next step

Inspect the learned weights from the "other agent" sensors to the attack
neurons in trained social agents. Then test learning with the social sensors
silenced, so that nearby agents cannot drive actions.
