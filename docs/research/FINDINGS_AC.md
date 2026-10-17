# Findings: Experiment AC — switching off the frustration drive does not let social agents learn in groups

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 training seeds
(3100–3111), agent 0 tested on 8 held-out worlds (9900–9907). Seeds and
worlds had never been run. Same design as [AB](FINDINGS_AB.md) without
hazards: 12 agents, 24 food, fixed dynamics, 1500 training ticks, no
evolution. Pre-registered at commit `791f53f`, spec unchanged, no
deviations. Run time 85 min.
Report: [`results/AC_frustration_drive/`](../../results/AC_frustration_drive/REPORT.md).

**Question.** In AB, learning barely paid among social peers and doubled the
attack rate. Two exploratory probes on spent AB seeds came first:

- [`attack_weights_probe.py`](../../tools/probes/attack_weights_probe.py):
  learning *lowered* the weight from the "other agent" sensors to attack
  (−0.11), so AB's candidate did not hold.
- [`frustration_probe.py`](../../tools/probes/frustration_probe.py): trained
  agents were more frustrated, and switching off the frustration-to-attack
  drive at test time cut their attacks from 0.17 to 0.05.

AC switches the drive off (`aggression_gain=0`) for the whole group, in
training and testing.

| Hypothesis | Test | Result |
|---|---|---|
| H48a: without the drive, learning pays among social peers | +0.59 [−2.06, 3.56] food per episode | not supported |
| H48b: removing the drive raises the learning gain | +0.21 [−3.94, 4.12] | not supported |
| H48c: with the drive, learning raises frustration | +0.098 [0.079, 0.118] | **supported** |
| H48d: removing the drive shrinks the learned rise in attacks | +0.002 [−0.058, 0.057] | not supported |
| H48e: without the drive, social and non-social peers' gains differ | −9.75 [−14.5, −5.0] | **difference detected** |

**By the pre-registered rule (H48a and H48b not supported), the frustration
drive does not explain why learning fails among social peers.**

| condition | trained | untrained | learning gain | trained attack rate | untrained attack rate | trained frustration | untrained frustration |
|---|---|---|---|---|---|---|---|
| social12 | 14.8 | 14.4 | +0.4 | 0.146 | 0.063 | 0.283 | 0.185 |
| social12, no drive | 16.6 | 16.0 | +0.6 | 0.101 | 0.016 | 0.254 | 0.167 |
| crowd12 (non-social) | 26.6 | 16.3 | +10.3 | — | — | 0.240 | 0.146 |

## Interpretation

- **The learned rise in attacks does not need the drive.** Without it,
  learning still raised the attack rate by the same amount (0.016 → 0.101,
  against 0.063 → 0.146 with it). The drive adds a roughly constant amount of
  attacking. The rise comes from the learned input weights.
- **Learning raises frustration in every group, including the non-social
  one where learning pays** (0.15 → 0.24). Frustration follows negative
  reward-prediction errors. A guess, not tested: trained agents eat more, so
  their reward expectation is higher and each tick without food is a larger
  negative error. Either way, the rise is not specific to social agents.
- **The probe misled.** Switching the drive off only at test time, after
  training with it, cut the attack rate. Switching it off for the whole run
  did not cut the learned rise. This is the second pilot this series that did
  not hold on new seeds (see [Y](FINDINGS_Y.md)).
- Both probes found that learning moves input weight away from sensors that
  are often active (food, other agents) and onto sensors that are silent or
  near-constant. This happens for every action, including in solo and
  non-social agents, where learning pays.

## Limits

- 1500 training ticks, agent 0 only, 8 test worlds, no hazards.
- Learning gains among social agents vary widely by seed (−8.5 to +13.6).

## Next step

Find which input weights carry the learned rise in attacks. An exploratory
probe, [`frozen_rows_probe.py`](../../tools/probes/frozen_rows_probe.py),
ran after AC on spent seeds 870–875 with 4 test worlds. It froze the input
weights of one group of actions during learning:

| what learns | learning gain | trained attack rate | untrained attack rate |
|---|---|---|---|
| all actions | +3.8 | 0.196 | 0.050 |
| movement only (social inputs frozen) | −2.4 | 0.291 | 0.050 |
| social only (movement inputs frozen) | +5.6 | 0.022 | 0.050 |

If this holds on new seeds, the rise in attacks comes from what learning
does to the movement neurons, not to the attack neurons. A candidate
consistent with the weight drift above: learning moves the movement
neurons' weight onto silent sensors, so they respond less to the inputs
they actually receive and the attack neurons win more often. This is the
pre-registered test in [AE](FINDINGS_AE.md).
