# Does a state-dependent critic, predicted by theory, rescue learning under alignment shaping?

**Question.** AF found that replacing alignment shaping with approach shaping rescues learning among social peers. tools/theory/shaping_covariance.py gives a general reason: for any stationary shaping potential Phi with lag-1 autocorrelation rho, the shaping reward r = Phi(t+1) - Phi(t) has Cov(Phi(t), r) = -(1 - rho) Var(Phi) <= 0. When presynaptic activity at decision time rises with Phi (food straight ahead drives the sensors hardest and maximises alignment), a covariance learning rule with a scalar reward baseline depresses active synapses on average, whatever the policy. The same derivation predicts a fix that keeps the shaping: a baseline that depends on the state, E[r | state], removes the term (checked numerically on an AR(1) potential: drift -0.30 with a scalar baseline, -0.001 with a state baseline). NeuralMind already has such a critic (critic='state': one reward expectation per binarised sensor state). This study tests the prediction without changing the reward.

Same design as AF: fixed dynamics (substeps=32, reset_each_decision, normalize with normalize_to='innate'), no hazards, 1500 training ticks, agent 0 tested frozen on 8 held-out worlds against a fresh untrained agent or group with the same config. Alignment shaping (the default reward) throughout except approach12. critic='state' keys the reward expectation on which of the 11 sensors exceed 0.2. Caveats fixed in advance: the state critic's states are coarse (binarised sensors), so it may remove only part of the bias; and the theory covers the shaping term only, not eating or social rewards. Interpretation rule, fixed in advance: the theory's fix works in NeuralMind if H60a and H60b are supported; it fully rescues social learning if H60c is also supported. No pilot was run. Seeds 3800-3811 and worlds 9940-9947 have never been run.

NeuralMind 0.2.0 · 2026-10-17 20:51 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/AM_state_critic.json` at commit `f99f83001ed98df1d52c5fe1ad7b253de031faeb` (2026-10-17T20:11:00+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H60a | Under alignment shaping, a state critic shrinks the learned rise in attacks among social peers | -0.08001 [-0.1542, -0.01232] | **supported** |
| H60b | Under alignment shaping, a state critic raises the learning gain among social peers | 6.208 [2.061, 9.875] | **supported** |
| H60c | Under alignment shaping with a state critic, learning pays among social peers | 6.719 [3.594, 9.552] | **supported** |
| H60d | A solo agent still learns under alignment shaping with a state critic | 13.04 [12.01, 14.12] | **supported** |
| H60e | Among social peers, the state critic under alignment shaping differs from approach shaping | 2.51 [-0.07318, 4.969] | **no difference detected** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| social12_scalar | 14.64 [11.9, 17.6] | 14.03 [12.54, 15.67] | 14.12 [14.12, 14.12] | 0.5104 [-2.22, 3.479] | 0.6042 [-2.261, 3.334] | 0 [0, 0] | 0.3773 [0.2936, 0.4584] |
| social12_state | 20.84 [17.72, 23.68] | 13.71 [12.68, 14.8] | 14.12 [14.12, 14.12] | 6.719 [3.594, 9.552] | 7.135 [3.646, 10.38] | 0 [0, 0] | 0.4346 [0.3286, 0.5394] |
| social12_approach | 18.33 [17.02, 19.68] | 15.44 [14.8, 16.03] | 14.12 [14.12, 14.12] | 4.208 [2.895, 5.552] | 2.896 [1.51, 4.271] | 0 [0, 0] | 0.385 [0.3458, 0.4275] |
| solo_scalar | 14.92 [13.37, 16.33] | 3.969 [3.416, 4.531] | 5.625 [5.625, 5.625] | 9.292 [7.75, 10.71] | 10.95 [9.375, 12.39] | 0 [0, 0] | 0.329 [0.2874, 0.3762] |
| solo_state | 18.67 [17.64, 19.75] | 4.844 [4.292, 5.438] | 5.625 [5.625, 5.625] | 13.04 [12.01, 14.12] | 13.82 [12.79, 14.9] | 0 [0, 0] | 0.367 [0.323, 0.4216] |



Full per-metric summaries and raw per-run data: `results.json`.