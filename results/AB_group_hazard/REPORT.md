# Does the hazard trap explain why learning fails among social peers?

**Question.** Z found that learning pays among 11 non-social peers (+6.9) but not among 11 social peers (-2.8). AA found that a lone social agent barely learns with hazards (+1.1) and learns without them (+6.2): its non-moving actions (attack, share, signal) keep it inside hazards. This study asks whether removing hazards also lets social agents learn in groups.

Same design as Z: fixed dynamics (substeps=32, reset_each_decision, normalize with normalize_to='innate'), 12 agents and 24 food, all agents train together for 1500 ticks, agent 0 is tested frozen among its frozen peers on 8 held-out worlds against a fresh untrained group. social12 repeats Z's social condition on new seeds; *_nohazard sets n_hazard=0. No pilot was run. Interpretation rule, fixed in advance: the hazard trap explains the group failure if H47a and H47b are supported; other social effects remain if H47c is also supported. Seeds 870-881 and worlds 9700-9707 have never been run.

NeuralMind 0.2.0 · 2026-10-17 07:28 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/AB_group_hazard.json` at commit `68dbe4b8ba6bf6614c37871a7bb2eb13431c4124` (2026-10-17T05:53:49+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H47a | Without hazards, learning pays among social peers | 0.2604 [-2.188, 2.927] | **not supported** |
| H47b | Removing hazards raises the learning gain among social peers | 2.271 [-1.803, 6.313] | **not supported** |
| H47c | Without hazards, social peers still gain less than non-social peers | -7.052 [-11.17, -2.875] | **supported** |
| H47d | Without hazards, learning does not raise the attack rate among social peers | 0.09239 [0.05087, 0.1369] | **difference detected** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| social12 | 8.99 [6.719, 11.61] | 7.958 [6.74, 8.938] | 11 [11, 11] | -2.01 [-4.281, 0.6146] | 1.031 [-1.459, 3.365] | 0 [0, 0] | 0.2505 [0.1756, 0.3317] |
| social12_nohazard | 15.01 [12.56, 17.68] | 12.41 [11.41, 13.39] | 14.75 [14.75, 14.75] | 0.2604 [-2.188, 2.927] | 2.604 [0.5833, 4.802] | 0 [0, 0] | 0.335 [0.2423, 0.435] |
| crowd12_nohazard | 24.69 [22.31, 27.14] | 16.82 [15.45, 18.05] | 17.38 [17.38, 17.38] | 7.312 [4.938, 9.761] | 7.865 [4.938, 11.07] | 0 [0, 0] | 0.4067 [0.3122, 0.506] |



Full per-metric summaries and raw per-run data: `results.json`.