# Is the learned rise in attacks carried by the movement neurons' input weights?

**Question.** In AB and AC, learning among social peers barely paid and raised the attack rate, with or without the frustration drive. An exploratory probe after AC (tools/probes/frozen_rows_probe.py) froze the input weights of one group of actions during learning. Freezing the social actions' inputs raised attacks further; freezing the movement actions' inputs removed the rise and gave the largest gain. This study tests that on new seeds.

Same design as AC's social12: fixed dynamics (substeps=32, reset_each_decision, normalize with normalize_to='innate'), 12 social agents, 24 food, no hazards, frustration drive on, all agents train together for 1500 ticks, agent 0 tested frozen among frozen peers on 8 held-out worlds against a fresh untrained group. frozen_inputs lists actions whose input weights never learn (they are still renormalised, which leaves frozen rows unchanged). Probe on spent seeds 870-875, 4 test worlds 9800-9803: learning gain +3.8 / -2.4 / +5.6 and trained attack rate 0.196 / 0.291 / 0.022 (untrained 0.050) for learn_all / freeze_social / freeze_moves. Interpretation rule, fixed in advance: learning in the movement neurons carries the rise in attacks if H51a and H51b are supported. H51c and H51d ask whether freezing movement inputs restores a learning gain. Seeds 3200-3211 and worlds 9920-9927 have never been run.

NeuralMind 0.2.0 · 2026-10-17 13:36 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/AE_which_weights.json` at commit `8f02a7b5bbef02daa15319e3f6ad491f0158bd92` (2026-10-17T12:18:33+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H51a | When only the movement inputs learn, learning raises the attack rate | 0.1963 [0.1663, 0.2305] | **supported** |
| H51b | Freezing the movement inputs shrinks the rise in attack rate that learning causes | -0.1172 [-0.1518, -0.08777] | **supported** |
| H51c | With the movement inputs frozen, learning pays among social peers | 2.615 [1.656, 3.5] | **supported** |
| H51d | Freezing the movement inputs raises the learning gain | -0.9062 [-3.667, 1.584] | **not supported** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| learn_all | 18.02 [15.71, 20.44] | 13.74 [12.5, 14.91] | 14.5 [14.5, 14.5] | 3.521 [1.208, 5.938] | 4.281 [2.042, 6.584] | 0 [0, 0] | 0.4259 [0.3692, 0.4862] |
| freeze_social | 10.21 [7.354, 13.49] | 13.18 [12.31, 14.27] | 14.5 [14.5, 14.5] | -4.292 [-7.146, -1.01] | -2.969 [-5.677, 0.1667] | 0 [0, 0] | 0.2796 [0.191, 0.3706] |
| freeze_moves | 17.11 [16.16, 18] | 15.71 [14.89, 16.57] | 14.5 [14.5, 14.5] | 2.615 [1.656, 3.5] | 1.406 [-0.2607, 2.958] | 0 [0, 0] | 0.3178 [0.3136, 0.3235] |



Full per-metric summaries and raw per-run data: `results.json`.