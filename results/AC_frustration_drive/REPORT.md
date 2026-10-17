# Does the frustration-to-attack drive cancel what social agents learn in groups?

**Question.** AB found that, without hazards, learning barely pays among social peers (+0.3) and more than doubles the attack rate. The candidate it named (other-agent sensors potentiating attack) did not hold in a probe: learning lowered those weights. A second probe pointed instead at the frustration drive: accumulated negative reward-prediction error adds a tonic current to the attack neurons, and trained agents were more frustrated than untrained ones. This study switches the drive off (aggression_gain=0) for the whole group, during training and testing.

Same design as AB: fixed dynamics (substeps=32, reset_each_decision, normalize with normalize_to='innate'), 12 agents and 24 food, no hazards, all agents train together for 1500 ticks, agent 0 is tested frozen among its frozen peers on 8 held-out worlds against a fresh untrained group with the same config. Exploratory probes on spent AB seeds 870-876 (tools/probes/attack_weights_probe.py, frustration_probe.py; test worlds 9800-9803): (1) learning lowered the mean weight from the other-agent sensors to attack (-0.11) and moved weight from active sensors (food, other agents) to silent ones in every condition, solo included; (2) test-time frustration was 0.28 trained vs 0.15 untrained and stayed 0.26 when no agent had the drive (agent 0 then attacked 5.0 times), so being attacked did not explain it; (3) the learning gain was +3.5 with the drive on and +6.0 with it off for the whole group at test only, with large seed-to-seed spread (-5.0 to +13.8). These probes used the drive only at test, not during training. Interpretation rule, fixed in advance: the frustration drive explains the group failure if H48a and H48b are supported. H48c tests the proposed route (learning raises frustration). Seeds 3100-3111 and worlds 9900-9907 have never been run.

NeuralMind 0.2.0 · 2026-10-17 11:40 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/AC_frustration_drive.json` at commit `791f53fd84ebcd1eea4e0407c68eb460e413a6b0` (2026-10-17T10:15:25+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H48a | Without the frustration drive, learning pays among social peers | 0.5938 [-2.063, 3.563] | **not supported** |
| H48b | Removing the frustration drive raises the learning gain among social peers | 0.2083 [-3.938, 4.115] | **not supported** |
| H48c | With the drive, learning raises test-time frustration among social peers | 0.09788 [0.07882, 0.1178] | **supported** |
| H48d | Removing the drive shrinks the rise in attack rate that learning causes | 0.00184 [-0.05782, 0.05657] | **not supported** |
| H48e | Without the drive, social peers' learning gain differs from non-social peers' | -9.75 [-14.5, -5.042] | **difference detected** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| social12 | 14.76 [11.5, 18.3] | 13.67 [12.01, 15.48] | 14.38 [14.38, 14.38] | 0.3854 [-2.876, 3.927] | 1.094 [-2.021, 4.188] | 0 [0, 0] | 0.3557 [0.2576, 0.4537] |
| social12_nodrive | 16.59 [13.94, 19.56] | 14.57 [13.53, 15.67] | 16 [16, 16] | 0.5938 [-2.063, 3.563] | 2.021 [-0.3438, 4.604] | 0 [0, 0] | 0.2976 [0.2064, 0.4077] |
| crowd12 | 26.59 [24.44, 29.18] | 17.64 [16.81, 18.59] | 16.25 [16.25, 16.25] | 10.34 [8.187, 12.93] | 8.958 [6.792, 11.66] | 0 [0, 0] | 0.4358 [0.3676, 0.5103] |



Full per-metric summaries and raw per-run data: `results.json`.