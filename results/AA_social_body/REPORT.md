# Why does a social agent fail to learn foraging even when it is alone?

**Question.** Z found that learning pays among non-social peers but not among social ones. An exploratory pilot then trained a social agent alone (social actions and sensors, no other agents) and it also failed to learn (trained 2.97 vs 15.25 food for a lone non-social agent, 6 seeds). Its social sensors read zero when alone, and it still chose movement in about 80% of ticks. A trace showed it entering a hazard and staying there, turning and attacking, losing 0.044 energy per tick until it died about 22 ticks into the episode. The social actions (attack, share, signal) do not move the body, so an agent whose learned response to a hazard is a non-moving action stays inside it. A second pilot (seeds 740-743) without hazards: learning gain +6.4 for the lone social agent vs +1.3 with hazards, and +10.3 vs +8.4 for the lone non-social agent.

All conditions use the W 'full' dynamics (substeps=32, reset_each_decision, normalize with normalize_to='innate'), a single agent, 1500 training ticks (3 episodes of 500), 16 held-out 500-tick test worlds. solo: non-social. social_alone: social=True, so 6 actions and 11 sensors, but no other agents. *_nohazard: n_hazard=0. learning_gain = trained_food - untrained_food. Interpretation rule, fixed in advance: hazards explain the social agent's failure if H46a and H46b are supported; the social body impairs learning beyond hazards if H46d is also supported. Seeds 850-861 and test worlds 9400-9415 have never been run.

NeuralMind 0.2.0 · 2026-10-17 05:52 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/AA_social_body.json` at commit `26791d30b74237a41c3417730d7ff26151188d3e` (2026-10-17T05:30:41+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H46a | Without hazards, a lone social agent's learning pays | 6.24 [4.578, 7.719] | **supported** |
| H46b | Removing hazards raises a lone social agent's learning gain | 5.12 [3.51, 6.589] | **supported** |
| H46c | Replication of the pilot: with hazards, a lone social agent gains less from learning than a lone non-social agent | -12.82 [-13.98, -11.46] | **supported** |
| H46d | Without hazards, a lone social agent still gains less than a lone non-social agent | -4.938 [-6.891, -3.297] | **supported** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| solo | 15.94 [14.7, 16.97] | 3.057 [2.667, 3.365] | 2 [2, 2] | 13.94 [12.7, 14.97] | 12.89 [11.48, 14.1] | 0 [0, 0] | 0.3253 [0.2881, 0.3627] |
| social_alone | 2.12 [1.693, 2.568] | 1.755 [1.625, 1.875] | 1 [1, 1] | 1.12 [0.6927, 1.568] | 0.3646 [-0.09896, 0.8542] | 0 [0, 0] | 0.2565 [0.2338, 0.2819] |
| solo_nohazard | 16.36 [15.33, 17.4] | 4.839 [4.385, 5.245] | 5.188 [5.188, 5.188] | 11.18 [10.14, 12.21] | 11.53 [10.67, 12.45] | 0 [0, 0] | 0.3133 [0.27, 0.36] |
| social_alone_nohazard | 10.24 [8.578, 11.72] | 3.49 [3.255, 3.703] | 4 [4, 4] | 6.24 [4.578, 7.719] | 6.75 [5.161, 8.182] | 0 [0, 0] | 0.316 [0.2926, 0.341] |



Full per-metric summaries and raw per-run data: `results.json`.