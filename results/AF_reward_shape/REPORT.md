# Does the alignment-shaping reward cause social agents' learned rise in attacks?

**Question.** AB, AC and the frozen-rows probe found that learning among social peers raises the attack rate through the movement neurons' input weights, which drift from active sensors onto silent ones. A probe (tools/probes/rpe_eligibility_probe.py, solo agents, seeds 11-13) found that under the default alignment-shaping reward the reward-prediction error is negatively correlated with total eligibility (r = -0.07 to -0.16), so active synapses are on average depressed and normalisation moves weight to silent inputs. Under approach shaping or eating reward only, the correlation was positive (+0.07 to +0.13). This study replaces alignment shaping with approach shaping.

Same design as AC/AE: fixed dynamics (substeps=32, reset_each_decision, normalize with normalize_to='innate'), no hazards, 1500 training ticks, agent 0 tested frozen on 8 held-out worlds against a fresh untrained agent or group with the same config. reward_mode='approach' rewards r_approach * (decrease in distance to the nearest food) instead of r_align * (increase in alignment with it). Exploratory pilot on spent seeds 870-873, 3 test worlds 9800-9802 (tools/probes/reward_shape_pilot.py): learning gain solo_align +11.4, solo_approach -0.3, social12_align +7.5, social12_approach +9.3; trained/untrained attack rate social12_align 0.174/0.052, social12_approach 0.057/0.052. The pilot's social12_align gain disagrees with AC (+0.4), so it is noisy. Interpretation rule, fixed in advance: alignment shaping causes the learned rise in attacks if H52a is supported; approach shaping rescues social learning if H52b and H52c are supported. H52d asks whether approach shaping supports learning at all in a solo agent; the pilot suggests it does not. Seeds 3300-3311 and worlds 9930-9937 have never been run.

NeuralMind 0.2.0 · 2026-10-17 14:00 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/AF_reward_shape.json` at commit `0e8b4d1ad7edad8a34cfbc1d0794b308ef1b7108` (2026-10-17T12:41:36+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H52a | With approach shaping, learning raises the attack rate less than with alignment shaping | -0.07783 [-0.1232, -0.04087] | **supported** |
| H52b | Approach shaping gives social peers a larger learning gain than alignment shaping | 5.948 [3.604, 8.459] | **supported** |
| H52c | With approach shaping, learning pays among social peers | 4.854 [3.552, 6.073] | **supported** |
| H52d | With approach shaping, learning pays for a solo agent | 1.948 [1.427, 2.521] | **supported** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| social12_align | 11.41 [9.134, 13.61] | 12.29 [10.99, 13.61] | 12.5 [12.5, 12.5] | -1.094 [-3.366, 1.115] | -0.8854 [-3.042, 1.396] | 0 [0, 0] | 0.3221 [0.256, 0.381] |
| social12_approach | 17.35 [16.05, 18.57] | 14.82 [13.85, 15.8] | 12.5 [12.5, 12.5] | 4.854 [3.552, 6.073] | 2.531 [0.9583, 4.105] | 0 [0, 0] | 0.3915 [0.3619, 0.4188] |
| solo_approach | 5.823 [5.302, 6.396] | 4.458 [3.969, 5.052] | 3.875 [3.875, 3.875] | 1.948 [1.427, 2.521] | 1.365 [0.6977, 2.125] | 0 [0, 0] | 0.3537 [0.3476, 0.3599] |



Full per-metric summaries and raw per-run data: `results.json`.