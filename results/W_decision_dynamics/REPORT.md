# Can lifetime learning find sensory foraging once decisions are slow, fresh and balanced?

**Question.** V found that evolving agents do not measurably use their senses, and P, R and T found that lifetime learning lowers foraging. Exploratory probes after V point to the decision dynamics: (1) state carries over between decisions, so the current winner keeps winning (an untrained agent repeats one action for a median of 217 of 500 ticks); (2) a decision lasts 8 ms against a 20 ms membrane time constant, so from rest sensory input barely reaches the action populations; (3) rewarded STDP runs away, so one pathway saturates (Skorheim, Lonjers & Bazhenov 2014). A 12-seed pilot that fixed all three together (32 ms decisions, state cleared before each decision, per-neuron input weights normalised) trained 12/12 single agents to 20.0 food per test episode with real senses vs 3.1 scrambled. Removing any one fix gave 1.3-4.4. This study tests that on fresh training seeds and fresh test worlds.

Each run trains one fresh agent for 40 episodes of 500 ticks (learning on, weights kept), freezes it, and tests it on 16 held-out worlds with real and scrambled food/hazard senses; an untrained agent with the same configuration is tested on the same worlds. trained_food is mean food per test episode; learning_gain = trained_food - untrained_food; sense_gain = trained_food - trained_food_scrambled; collapsed01 = 1 if trained_food < 1. Conditions: default (8 ms, state carried, no normalisation); full (substeps=32, reset_each_decision, normalize); no_reset, no_window and no_norm each remove one fix from full. Interpretation rule, fixed in advance: the fixes make lifetime learning work if H38a, H38b and H38c are supported; an ingredient is necessary if its H38d/e/f test is supported. Pilot numbers (training seeds 500-511, test worlds 9000-9015) are exploratory and not part of this test. Training seeds 600-611 and test worlds 9100-9115 have never been run.

NeuralMind 0.2.0 · 2026-10-16 23:35 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/W_decision_dynamics.json` at commit `2bfa1cf619335d63433fd299a1817dbacb3e9c37` (2026-10-16T22:54:37+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H38a | Trained agents with all three fixes eat more than trained agents with the default dynamics | 15.86 [14.12, 17.24] | **supported** |
| H38b | With all three fixes, lifetime learning pays: trained agents eat more than untrained ones | 15.42 [14.29, 16.48] | **supported** |
| H38c | With all three fixes, trained agents use their senses: they eat more with real than with scrambled senses | 15.93 [14.78, 16.97] | **supported** |
| H38d | Clearing state before each decision is necessary (full beats no_reset) | 16.72 [15.17, 18.07] | **supported** |
| H38e | A 32 ms decision window is necessary (full beats no_window) | 15.07 [13.74, 16.27] | **supported** |
| H38f | Weight normalisation is necessary (full beats no_norm) | 15.89 [14.43, 17.28] | **supported** |
| H38g | Replication: with the default dynamics, learning raises foraging over untrained agents | -0.6875 [-1.646, 0.3178] | **not supported** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| default | 2.812 [1.854, 3.818] | 2.026 [1.349, 2.74] | 3.5 [3.5, 3.5] | -0.6875 [-1.646, 0.3178] | 0.7865 [0.1456, 1.562] | 0.1667 [0, 0.4167] | 0.2011 [0.1393, 0.2646] |
| full | 18.67 [17.54, 19.73] | 2.745 [2.354, 3.188] | 3.25 [3.25, 3.25] | 15.42 [14.29, 16.48] | 15.93 [14.78, 16.97] | 0 [0, 0] | 0.06658 [0.06015, 0.07258] |
| no_reset | 1.953 [1.109, 2.912] | 2.031 [1.589, 2.464] | 1.438 [1.438, 1.438] | 0.5156 [-0.3284, 1.474] | -0.07812 [-0.9688, 0.9064] | 0.4167 [0.1667, 0.6667] | 0.2871 [0.1825, 0.3996] |
| no_window | 3.604 [3.292, 3.932] | 2.99 [2.651, 3.271] | 2.562 [2.562, 2.562] | 1.042 [0.729, 1.37] | 0.6146 [0.1094, 1.13] | 0 [0, 0] | 0.3401 [0.3359, 0.3446] |
| no_norm | 2.781 [1.146, 4.615] | 1.276 [0.5938, 2.057] | 3.25 [3.25, 3.25] | -0.4688 [-2.104, 1.365] | 1.505 [0.5311, 2.646] | 0.5 [0.25, 0.75] | 0.1379 [0.06119, 0.2188] |



Full per-metric summaries and raw per-run data: `results.json`.